from matplotlib import pyplot as plt
from plotly.subplots import make_subplots
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

from keyforge.dataframes import SETS, HOUSES, set_house_df


def plot_deck_overview(deck_df):
    """Plot number of decks per house/stat as heatmap"""
    fig = px.imshow(set_house_df(deck_df), text_auto=True, color_continuous_scale="RdYlGn", width=700, height=500)
    fig.update(layout_coloraxis_showscale=False)
    return fig


def plot_time_changes(match_df):
    """Plot changes in decks/matches over time"""
    fig = make_subplots(rows=1, cols=4, horizontal_spacing=0.08)

    # Year for each match:
    years = [int(d[0:4]) for d in match_df["date"]]

    # Plots:
    fig.add_trace(go.Scatter(x=match_df["time"], y=match_df["number_decks"]), row=1, col=1)
    fig.add_trace(go.Histogram(x=years), row=1, col=2)
    fig.add_trace(go.Scatter(x=match_df["time"], y=match_df["cumulative_matches"]), row=1, col=3)
    fig.add_trace(go.Scatter(x=match_df["time"], y=match_df["perc_completion"]), row=1, col=4)

    # Style axes:
    ticks = list(set(years))
    axis_labels = [
        "Number of owned decks",
        "Number of matches",
        "Cumulative number of matches",
        "Cumulative percentage completion"
    ]
    for idx, txt in enumerate(axis_labels):
        fig.update_xaxes(tickvals = ticks, ticktext = ticks, mirror="allticks", row=1, col=idx+1)
        fig.update_yaxes(title_text=txt, mirror="allticks", row=1, col=idx+1)

    # Misc styling:
    fig.update_layout(
        autosize=False,
        width=1500,
        height=500,
        template="simple_white",
        showlegend=False
    )

    return fig


def plot_match_results(match_hm):
    """Plot results of matches as heatmap"""
    fig = px.imshow(match_hm, text_auto=True, color_continuous_scale="RdYlGn", width=1400, height=1400)
    fig.update(layout_coloraxis_showscale=False)
    return fig


def plot_deck_stats(deck_df):
    """Plot deck stats as heatmap"""
    
    data = deck_df.iloc[:,[7, 11, 12, 13]]
    data.index = [f"{idx}: {row[0]} ({row[1]} - {row[2]} / {row[3]} / {row[4]})" for idx, row in deck_df.iterrows()]
    fig = px.imshow(data, text_auto=True, color_continuous_scale="RdYlGn", aspect="auto", width=900, height=1200)
    fig.update(layout_coloraxis_showscale=False)
    return fig


def plot_win_vs_sas(deck_df):
    """Plot for each deck win% vs SAS (color by set) + trendline"""

    # Plot data:
    fig = px.scatter(
        deck_df,
        x="SAS",
        y="win_rate",
        color="set",
        color_discrete_map=SETS,
        size="plays",
        hover_data=["name"],
        width=800,
        height=600,
        template="simple_white"
    )

    # Plot trendline + R2
    x = list(deck_df.loc[deck_df["win_rate"].notnull(), "SAS"])
    y = list(deck_df.loc[deck_df["win_rate"].notnull(), "win_rate"])
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    fig.add_scatter(
        x=[min(x), max(x)],
        y=[p(min(x)), p(max(x))],
        mode="lines",
        line={"color":"grey"},
        showlegend=False
    )

    # Plot formatting
    fig.update_xaxes(title_text="SAS", mirror="allticks")
    fig.update_yaxes(title_text="Win rate [%]", range=[0, 100], mirror="allticks")
    
    return fig


def plot_group_heatmaps(group_df, group_plays_hm, group_wins_hm, fig_length):
    """Group heatmaps: stats - match plays - match win rates"""
    fig = make_subplots(rows=1, cols=3, horizontal_spacing=0.08)

    # Filter first heatmap:
    filtered_df = group_df.iloc[:,[0, 1, 5, 6, 7, 8]]

    # Plot heatmaps:
    for idx, df in enumerate([filtered_df, group_plays_hm, group_wins_hm]):
        fig.add_trace(go.Heatmap(
            z=df[::-1].values,
            x=df[::-1].columns,
            y=df[::-1].index,
            colorscale="RdYlGn",
            showscale=False,
            text=df[::-1].values,
            texttemplate="%{text}",
        ), row=1, col=idx+1)

    # Adjust layout for subplots
    fig.update_layout(
        height=600,  # fixed height
        width=fig_length,  # dynamic length
        template="plotly_white"
    )

    return fig


def plot_set_trends(set_df):
    """Set plots: Average win rates vs SAS - Changes in SAS overtime - Changes in win rate overtime"""
    fig , ax = plt.subplots(1, 3, figsize=(20,6))

    # Average win rates vs SAS (color by set):
    for deck_set in SETS:
        x = set_df.loc[deck_set, "avg_deck_sas"]
        y = set_df.loc[deck_set, "avg_deck_win_rate"]
        yerr = set_df.loc[deck_set, "std_deck_win_rate"]
        ax[0].scatter(x, y, c=SETS[deck_set], label = deck_set)
        ax[0].errorbar(x, y, yerr=yerr, fmt="-o", color=SETS[deck_set])
    win_sas_plot_settings(ax[0], xlim=[50, 80])

    # Changes in SAS overtime:
    ax[1].plot(set_df.index, set_df["avg_deck_sas"])
    ax[1].set_ylabel("SAS")
    ax[1].set_ylim(ymin=50, ymax=80)

    # Changes in win rate overtime:
    ax[2].plot(set_df.index, set_df["win_rate"])
    ax[2].set_ylabel("Win rate [%]")
    _ = ax[2].set_ylim(ymin=20, ymax=80)

    return fig


def plot_house_trends(house_df):
    """House plot: Average win rates vs SAS"""
    fig , ax = plt.subplots(1, 1, figsize=(15,5))

    for deck_house in HOUSES:
        x = house_df.loc[deck_house, "avg_deck_sas"]
        y = house_df.loc[deck_house, "avg_deck_win_rate"]
        yerr = house_df.loc[deck_house, "std_deck_win_rate"]
        ax.scatter(x, y, c=HOUSES[deck_house], label = deck_house)
        ax.errorbar(x, y, yerr=yerr, fmt="-o", color=HOUSES[deck_house])

    win_sas_plot_settings(ax, xlim=[60, 90])

    return fig


def win_sas_plot_settings(ax, xlim=None):
    """Misc settings for win rate Vs SAS plots"""
    ax.set_xlabel("SAS")
    ax.set_ylabel("Win rate [%]")
    if xlim:
        ax.set_xlim(xmin=xlim[0], xmax=xlim[1])
    ax.set_ylim(ymin=0, ymax=100)
    ax.legend()
