from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from keyforge.dataframes import SETS, HOUSES, set_house_df


def plot_deck_overview(deck_df):
    """Plot number of decks per house/stat as heatmap"""

    plt.figure(figsize = (12,3))
    _ = sns.heatmap(set_house_df(deck_df), cmap="RdYlGn", annot=True, cbar=False)


def plot_time_changes(match_df):
    """Plot changes in decks/matches over time"""

    _ , ax = plt.subplots(1, 4, figsize=(24,6))

    # Number of decks over time:
    ax[0].plot(pd.to_datetime(match_df["date"]), match_df["number_decks"])
    ax[0].set_ylabel("Number of decks owned")

    # Cumulative distribution over time:
    ax[1].plot(pd.to_datetime(match_df["date"]), match_df["cumulative_matches"])
    ax[1].set_ylabel("Cumulative number of matches")

    # Matches per year:
    years = [int(d[0:4]) for d in match_df["date"]]
    ax[2].hist(years, bins=len(set(years)), range=[min(years)-0.5,max(years)+0.5], rwidth=0.6, align="mid")
    ax[2].set_ylabel("Number of matches")
    ax[2].set_xlim(xmin=min(years)-0.5, xmax=max(years)+0.5)

    # Cumulative percentage completion over time:
    ax[3].plot(pd.to_datetime(match_df["date"]), match_df["perc_completion"])
    ax[3].set_ylabel("Cumulative percentage completion")
    plt.show()


def plot_match_results(match_hm):
    """Plot results of matches as heatmap"""

    plt.figure(figsize = (16,16))
    _ = sns.heatmap(match_hm, cmap="RdYlGn", square=True, annot=True, cbar=False)


def plot_deck_stats(deck_df):
    """Plot deck stats as heatmap"""

    plt.figure(figsize = (10,10))
    deck_labels = [f"{idx}: {row[0]} ({row[1]} - {row[2]} / {row[3]} / {row[4]})" for idx, row in deck_df.iterrows()]
    _ = sns.heatmap(deck_df.iloc[:,[7, 11, 12, 13]], yticklabels=deck_labels , cmap="RdYlGn", annot=True, fmt="g", cbar=False)


def plot_win_vs_sas(deck_df):
    """Plot for each deck win% vs SAS (color by set) + trendline"""

    _ , ax = plt.subplots(1, figsize=(10,6))

    # Plot data:
    for deck_set in SETS:
        deck_sas = deck_df.loc[deck_df["set"] == deck_set, "SAS"]
        deck_win_rate = deck_df.loc[deck_df["set"] == deck_set, "win_rate"]
        set_data = ax.scatter(deck_sas, deck_win_rate, c=SETS[deck_set], label = deck_set, zorder = 10)
        set_data.set_clip_on(False)

    # Plot trendline + R2
    x = list(deck_df.loc[deck_df["win_rate"].notnull(), "SAS"])
    y = list(deck_df.loc[deck_df["win_rate"].notnull(), "win_rate"])
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    ax.plot(x, p(x), color="grey", linewidth=0.5)

    plt.xlabel("SAS")
    plt.ylabel("Win rate [%]")
    ax.set_ylim(ymin=0, ymax=100)
    plt.legend()
    plt.show()


def plot_set_heatmaps(set_df, set_plays_hm, set_wins_hm):
    """Set heatmaps: stats - match plays - match win rates"""

    _ , (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18,6))

    filtered_df = set_df.iloc[:,[0, 1, 5, 6, 7, 8]]
    _ = sns.heatmap(filtered_df, cmap="RdYlGn", ax=ax1, square=True, annot=True, fmt="g", cbar=False)
    _ = sns.heatmap(set_plays_hm, cmap="RdYlGn", ax=ax2, square=True, annot=True, fmt="g", cbar=False)
    _ = sns.heatmap(set_wins_hm, cmap="RdYlGn", ax=ax3, square=True, annot=True, fmt="g", cbar=False)


def plot_set_trends(set_df):
    """Set plots: Average win rates vs SAS - Changes in SAS overtime - Changes in win rate overtime"""

    _ , ax = plt.subplots(1, 3, figsize=(20,6))

    # Average win rates vs SAS (color by set):
    for deck_set in SETS:
        x = set_df.loc[deck_set, "avg_deck_sas"]
        y = set_df.loc[deck_set, "avg_deck_win_rate"]
        yerr = set_df.loc[deck_set, "std_deck_win_rate"]
        ax[0].scatter(x, y, c=SETS[deck_set], label = deck_set)
        ax[0].errorbar(x, y, yerr=yerr, fmt="-o", color=SETS[deck_set])

    ax[0].set_xlabel("SAS")
    ax[0].set_ylabel("Win rate [%]")
    ax[0].set_xlim(xmin=50, xmax=80)
    ax[0].set_ylim(ymin=0, ymax=100)
    ax[0].legend()

    # Changes in SAS overtime:
    ax[1].plot(set_df.index, set_df["avg_deck_sas"])
    ax[1].set_ylabel("SAS")
    ax[1].set_ylim(ymin=50, ymax=80)

    # Changes in win rate overtime:
    ax[2].plot(set_df.index, set_df["win_rate"])
    ax[2].set_ylabel("Win rate [%]")
    _ = ax[2].set_ylim(ymin=20, ymax=80)


def plot_house_heatmaps(house_df, house_plays_hm, house_wins_hm):
    """House heatmaps: stast - match plays - match win rates"""

    _ , (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(22,6))

    filtered_df = house_df.iloc[:,[0, 1, 5, 6, 7, 8]]
    _ = sns.heatmap(filtered_df, cmap="RdYlGn", ax=ax1, square=True, annot=True, fmt="g", cbar=False)
    _ = sns.heatmap(house_plays_hm, cmap="RdYlGn", ax=ax2, square=True, annot=True, fmt="g", cbar=False)
    _ = sns.heatmap(house_wins_hm, cmap="RdYlGn", ax=ax3, square=True, annot=True, fmt="g", cbar=False)


def plot_house_trends(house_df):
    """House plot: Average win rates vs SAS"""

    _ , ax = plt.subplots(1, 1, figsize=(15,5))

    for deck_house in HOUSES:
        x = house_df.loc[deck_house, "avg_deck_sas"]
        y = house_df.loc[deck_house, "avg_deck_win_rate"]
        yerr = house_df.loc[deck_house, "std_deck_win_rate"]
        ax.scatter(x, y, c=HOUSES[deck_house], label = deck_house)
        ax.errorbar(x, y, yerr=yerr, fmt="-o", color=HOUSES[deck_house])

    ax.set_xlabel("SAS")
    ax.set_ylabel("Win rate [%]")
    ax.set_xlim(xmin=60, xmax=80)
    ax.set_ylim(ymin=0, ymax=100)
    ax.legend()
    plt.show()
