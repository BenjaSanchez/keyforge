import math
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp

from keyforge.dataframes import SETS, HOUSES, set_house_df


def plot_deck_overview(deck_df):
    """Plot number of decks per house/stat as heatmap"""
    fig = px.imshow(
        set_house_df(deck_df),
        text_auto=True,
        color_continuous_scale="RdYlGn",
        width=800,
        height=600
    )
    fig.update(layout_coloraxis_showscale=False)
    fig.update_traces(hovertemplate="<b>Set:</b> %{y}<br><b>House:</b> %{x}<extra></extra>")
    return fig


def plot_time_changes(match_df):
    """Plot changes in decks/matches over time"""
    fig = sp.make_subplots(rows=1, cols=4, horizontal_spacing=0.08)

    # Year for each match:
    years = [int(d[0:4]) for d in match_df["date"]]

    # Plots:
    fig.add_trace(go.Scatter(
        x=match_df["time"],
        y=match_df["number_decks"],
        hovertemplate=(
            "<b>Date:</b> %{x}<br>"
            "<b>Number of decks:</b> %{y}<extra></extra>"
            )
    ), row=1, col=1)
    fig.add_trace(go.Histogram(
        x=years,
        hovertemplate=(
            "<b>Year:</b> %{x}<br>"
            "<b>Number of matches:</b> %{y}<extra></extra>"
        )
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=match_df["time"],
        y=match_df["cumulative_matches"],
        hovertemplate=(
            "<b>Date:</b> %{x}<br>"
            "<b>Cumulative matches:</b> %{y}<extra></extra>"
        )
    ), row=1, col=3)
    fig.add_trace(go.Scatter(
        x=match_df["time"],
        y=match_df["perc_completion"],
        hovertemplate=(
            "<b>Date:</b> %{x}<br>"
            "<b>Percentage completion:</b> %{y}%<extra></extra>"
        )
    ), row=1, col=4)

    # Style axes:
    ticks = list(set(years))
    axis_labels = [
        "Number of owned decks",
        "Number of matches",
        "Cumulative number of matches",
        "Cumulative percentage completion"
    ]
    for idx, txt in enumerate(axis_labels):
        fig.update_xaxes(tickvals = ticks, ticktext = ticks, row=1, col=idx+1)
        scatter_settings(fig, ylabel=txt, column=idx+1)

    # Misc styling:
    fig.update_layout(autosize=False, width=1500, height=600, showlegend=False)

    return fig


def plot_match_results(match_hm):
    """Plot results of matches as heatmap"""
    fig = px.imshow(match_hm, text_auto=True, color_continuous_scale="RdYlGn", width=1500, height=1500)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_traces(hovertemplate=(
        "<b>Keys forged by:</b> %{y}<br>"
        "<b>Against:</b> %{x}<extra></extra>"
    ))
    return fig


def plot_deck_stats(deck_df):
    """Plot deck stats as heatmap"""
    
    data = deck_df.iloc[:,[7, 11, 12, 13]]
    data.index = [
        f"{idx}: {row[0]} ({row[1]} - {row[2]} / {row[3]} / {row[4]})" for idx, row in deck_df.iterrows()
    ]
    fig = px.imshow(
        data,
        text_auto=True,
        color_continuous_scale="RdYlGn",
        aspect="auto",
        width=900,
        height=1200
    )
    fig.update(layout_coloraxis_showscale=False)
    fig.update_traces(hovertemplate="Deck %{y}<br>Parameter: %{x}<extra></extra>")
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
        height=600
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
        showlegend=False,
        hoverinfo='skip'
    )

    # Customize plot:
    scatter_settings(fig, xlabel="SAS", ylabel="Win rate [%]", yrange=[0, 100], column=None)

    return fig


def plot_group_heatmaps(group_df, group_plays_hm, group_wins_hm):
    """Group heatmaps: stats - match plays - match win rates"""
    fig = sp.make_subplots(rows=1, cols=3, horizontal_spacing=0.08)

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
            hovertemplate=(
                "<b>row:</b> %{y}<br>"
                "<b>column:</b> %{x}<extra></extra>"
            )
        ), row=1, col=idx+1)

    # Customize plot:
    fig.update_layout(height=600, width=1500, template="none")

    return fig


def plot_house_trends(house_df):
    """House plot: Average win rates vs SAS"""
    fig = go.Figure()

    # Add values one house at a time:
    for deck_house in HOUSES:
        x = house_df.loc[deck_house, "avg_deck_sas"]
        y = house_df.loc[deck_house, "avg_deck_win_rate"]
        yerr = house_df.loc[deck_house, "std_deck_win_rate"]
        plays = int(house_df.loc[deck_house, "plays"])

        # Add data:
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode="markers",
            marker=dict(color=HOUSES[deck_house], size=math.sqrt(plays)),
            name=f"{deck_house}",
            hovertemplate=(
                f"<b>House:</b> {deck_house}<br>"
                f"<b>SAS:</b> {x}<br>"
                f"<b>Win Rate:</b> {y}%<br>"
                f"<b>Plays:</b> {plays}<extra></extra>"
            )
        ))

        # Add error bars:
        fig.add_trace(go.Scatter(
            x=[x, x],
            y=[y - yerr, y + yerr],
            mode="lines",
            line=dict(color=HOUSES[deck_house]),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Customize plot:
    fig.update_layout(height=600, width=1200, legend_title_text="Houses")
    scatter_settings(fig, xlabel="SAS", xrange=[60, 90], ylabel="Win Rate [%]", yrange=[0, 100])

    return fig


def plot_set_trends(set_df):
    """Set plots: Average win rates vs SAS - Changes in SAS overtime - Changes in win rate overtime"""
    fig = sp.make_subplots(rows=1, cols=3, horizontal_spacing=0.08)

    # Average win rates vs SAS (color by set):
    for deck_set in SETS:
        x = set_df.loc[deck_set, "avg_deck_sas"]
        y = set_df.loc[deck_set, "avg_deck_win_rate"]
        yerr = set_df.loc[deck_set, "std_deck_win_rate"]

        # Scale plays with sqrt() function:
        set_df.loc[deck_set, "scaled_plays"] = math.sqrt(set_df.loc[deck_set, "plays"])

        # Add data:
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode="markers",
            marker=dict(color=SETS[deck_set], size=set_df.loc[deck_set, "scaled_plays"]),
            name=f"{deck_set}",
            hovertemplate=(
                f"<b>Set:</b> {deck_set}<br>"
                f"<b>SAS:</b> {x}<br>"
                f"<b>Win Rate:</b> {y}%<br>"
                f"<b>Plays:</b> {int(set_df.loc[deck_set, 'plays'])}<extra></extra>"
            )
        ), row=1, col=1)

        # Add error bars:
        fig.add_trace(go.Scatter(
            x=[x, x],
            y=[y - yerr, y + yerr],
            mode="lines",
            line=dict(color=SETS[deck_set]),
            showlegend=False,
            hoverinfo='skip'
        ), row=1, col=1)

    # Changes in SAS overtime:
    fig.add_trace(go.Scatter(
        x=set_df.index,
        y=set_df["avg_deck_sas"],
        name="Avg SAS Over Time",
        line=dict(color="blue"),
        marker=dict(color="blue", opacity=1, size=set_df["scaled_plays"]),
        hovertemplate=(
            "<b>Set:</b> %{x}<br>"
            "<b>Avg SAS:</b> %{y}<extra></extra>"
        ),
        showlegend=False
    ), row=1, col=2)

    # Changes in win rate overtime:
    fig.add_trace(go.Scatter(
        x=set_df.index,
        y=set_df["win_rate"],
        name="Win Rate Over Time",
        line=dict(color="green"),
        marker=dict(color="green", opacity=1, size=set_df["scaled_plays"]),
        hovertemplate=(
            "<b>Set:</b> %{x}<br>"
            "<b>Avg Win Rate:</b> %{y}%<extra></extra>"
        ),
        showlegend=False
    ), row=1, col=3)

    # Customize plots:
    fig.update_layout(height=600, width=1500, legend_title_text="Sets")
    scatter_settings(fig, xlabel="SAS", xrange=[50, 80], ylabel="Win Rate [%]", yrange=[0, 100], column=1)
    scatter_settings(fig, ylabel="SAS", yrange=[50, 80], column=2)
    scatter_settings(fig, ylabel="Win Rate [%]", yrange=[0, 100], column=3)

    return fig


def scatter_settings(fig, xlabel=None, xrange=None, ylabel=None, yrange=None, column=None):
    """Miscelaneous settings for scatter plots"""
    fig.update_layout(template="simple_white")
    s = f", row=1, col={column}" if column else ""
    eval(f"fig.update_yaxes(mirror='allticks'{s})")
    eval(f"fig.update_xaxes(mirror='allticks'{s})")
    if xlabel:
        eval(f"fig.update_xaxes(title_text='{xlabel}'{s})")
    if xrange:
        eval(f"fig.update_xaxes(range={xrange}{s})")
    if ylabel:
        eval(f"fig.update_yaxes(title_text='{ylabel}'{s})")
    if yrange:
        eval(f"fig.update_yaxes(range={yrange}{s})")
