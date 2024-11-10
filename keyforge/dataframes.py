import numpy as np
import pandas as pd


SETS = {
    "CotA": "firebrick",
    "AoA": "mediumblue",
    "WC": "darkviolet",
    "MM": "black",
    "DT": "deepskyblue",
    "WoE": "olivedrab",
    "GR": "red",
    "AS": "gold",
}

HOUSES = {
    "brobnar": "darkorange",
    "dis": "magenta",
    "logos": "deepskyblue",
    "mars": "yellowgreen",
    "sanctum": "mediumblue",
    "shadows": "grey",
    "untamed": "darkgreen",
    "star alliance": "gold",
    "saurian": "aquamarine",
    "unfathomable": "blueviolet",
    "ekwidon": "red",
    "geistoid": "black",
    "skyborn": "lightsteelblue",
}


def deck_df(path="./decks.csv"):
    """Dataframe with all deck information"""
    return pd.read_csv(path, index_col=0)


def match_df(path="./matches.csv"):
    """Dataframe with all matches' information"""
    match_df = pd.read_csv(path)
    entry_dates = pd.to_datetime(deck_df()["entry_date"])

    # Add new columns to match df:
    for idx in match_df.index:
        cumulative_matches = idx + 1
        num_decks = sum([pd.to_datetime(match_df.loc[idx, "date"]) >= d for d in entry_dates])
        possible_matches = num_decks * (num_decks - 1) / 2
        match_df.loc[idx, "cumulative_matches"] = int(cumulative_matches)
        match_df.loc[idx, "number_decks"] = int(num_decks)
        match_df.loc[idx, "possible_matches"] = int(possible_matches)
        match_df.loc[idx, "perc_completion"] = round(cumulative_matches / possible_matches * 100, 1)
    
    return match_df


def set_house_df(deck_df):
    """Dataframe counting houses per set"""
    set_house_df = pd.DataFrame(0, index=SETS.keys(), columns=HOUSES.keys())

    for _, row in deck_df.iterrows():
        for house in row[2:5]:
            set_house_df.loc[row[1], house] += 1
    
    return set_house_df


def match_hm(deck_df, match_df):
    """Dataframe with match results as a 1v1 grid"""
    match_hm = pd.DataFrame(index=deck_df.index, columns=deck_df.index)

    for _, row in match_df.iterrows():
        match_hm.loc[row[1], row[2]] = row[3]
        match_hm.loc[row[2], row[1]] = row[4]
    match_hm.fillna(-1, inplace=True)
    
    return match_hm


def compute_stats(source_df, idx):
    """Compute statistics for specific deck/group as dictionary"""
    stats = {}
    if idx in source_df.index:
        # Calculate stats (for deck_df):
        stats["plays"] = sum(source_df.loc[idx,:] > -1)
        stats["wins"] = sum(source_df.loc[idx,:] == 3)
        stats["keys_forged"] = sum(source_df.loc[idx, source_df.loc[idx,:] > -1])
        keys_lost = sum(source_df.loc[source_df.loc[:,idx] > -1, idx])
        stats["key_diff"] = stats["keys_forged"] - keys_lost
    else:
        # Compute aggregated stats (for group_df):
        stats["plays"] = sum(source_df["plays"])
        stats["wins"] = sum(source_df["wins"])
        stats["keys_forged"] = sum(source_df["keys_forged"])
        stats["key_diff"] = sum(source_df["key_diff"])

    if stats["plays"] > 0:
        stats["win_rate"] = round(stats["wins"] / stats["plays"] * 100, 1)
        stats["avg_keys_forged"] = round(stats["keys_forged"] / stats["plays"], 1)
        stats["avg_key_diff"] = round(stats["key_diff"] / stats["plays"], 1)

    return stats


def add_deck_stats(deck_df, match_hm):
    """Add statistics to deck dataframe"""
    for idx in deck_df.index:
        for key, value in compute_stats(match_hm, idx).items():
            deck_df.loc[idx, key] = value


def group_df(deck_df, group):
    """Dataframe with group (house or set) statistics"""
    group_df = pd.DataFrame(index=SETS.keys() if group=="set" else HOUSES.keys())

    for idx in group_df.index:
        # Find decks from group:
        if group == "set":
            decks_from_group = deck_df["set"] == idx
        elif group == "house":
            decks_from_group = sum([deck_df[f"house{i}"] == idx for i in [1,2,3]]) == 1
        else:
            raise TypeError("Group should be set or house.")
        
        # Count number of decks from group:
        group_df.loc[idx, "decks"] = sum(decks_from_group)

        # Add aggregated statistics:
        for key, value in compute_stats(deck_df.loc[decks_from_group, :], idx).items():
            group_df.loc[idx, key] = value

        # Compute average deck performance stats:
        group_df.loc[idx, "avg_deck_sas"] = round(np.mean(deck_df.loc[decks_from_group, "SAS"]), 1)
        group_df.loc[idx, "avg_deck_win_rate"] = round(np.mean(deck_df.loc[decks_from_group, "win_rate"]), 1)
        group_df.loc[idx, "std_deck_win_rate"] = round(np.std(deck_df.loc[decks_from_group, "win_rate"]), 1)
        
    return group_df


def group_hms(group_df, deck_df, match_hm, group):
    """Dataframes with number of plays and win rate per group (house or set) against each other"""
    group_plays_hm = pd.DataFrame(0, index=group_df.index, columns=group_df.index)
    group_wins_hm = pd.DataFrame(0, index=group_df.index, columns=group_df.index)
    for group_1 in group_df.index:
        for group_2 in group_df.index:

            if group == "set":
                decks_1 = deck_df.index[deck_df["set"] == group_1]
                decks_2 = deck_df.index[deck_df["set"] == group_2]
            elif group == "house":
                decks_1 = deck_df.index[sum([deck_df[f"house{i}"] == group_1 for i in [1,2,3]]) == 1]
                decks_2 = deck_df.index[sum([deck_df[f"house{i}"] == group_2 for i in [1,2,3]]) == 1]
            else:
                raise TypeError("Group should be set or house.")
            
            plays = (match_hm.loc[decks_1, decks_2] > -1).sum().sum()
            wins = (match_hm.loc[decks_1, decks_2] == 3).sum().sum()
            win_rate = round(wins/plays*100) if plays > 0 else -1
            group_plays_hm.loc[group_1, group_2] = plays
            group_wins_hm.loc[group_1, group_2] = win_rate
    
    return (group_plays_hm, group_wins_hm)
