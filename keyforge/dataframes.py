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


def add_deck_stats(deck_df, match_hm):
    """Add statistics to deck dataframe"""

    for idx in deck_df.index:
        # Calculate stats:
        plays = sum(match_hm.loc[idx,:] > -1)
        wins = sum(match_hm.loc[idx,:] == 3)
        keys_forged = sum(match_hm.loc[idx, match_hm.loc[idx,:] > -1])
        keys_lost = sum(match_hm.loc[match_hm.loc[:,idx] > -1, idx])

        # Update dataframe:
        deck_df.loc[idx, "plays"] = plays
        deck_df.loc[idx, "wins"] = wins
        deck_df.loc[idx, "keys_forged"] = keys_forged
        deck_df.loc[idx, "key_diff"] = keys_forged - keys_lost
        try:
            deck_df.loc[idx, "win_rate"] = round(wins / plays * 100, 1)
            deck_df.loc[idx, "avg_keys_forged"] = round(keys_forged / plays, 1)
            deck_df.loc[idx, "avg_key_diff"] = round((keys_forged - keys_lost) / plays, 1)
        except ZeroDivisionError:
            pass


def set_df(deck_df):
    """Dataframe with set statistics"""

    set_df = pd.DataFrame(index=SETS.keys())
    for idx in set_df.index:
        # Compute aggregated stats:
        decks_in_set = deck_df["set"] == idx
        decks = sum(decks_in_set)
        plays = sum(deck_df.loc[decks_in_set, "plays"])
        wins = sum(deck_df.loc[decks_in_set, "wins"])
        keys_forged = sum(deck_df.loc[decks_in_set, "keys_forged"])
        key_diff = sum(deck_df.loc[decks_in_set, "key_diff"])

        # Add stats to dataframe:
        set_df.loc[idx, "decks"] = decks
        set_df.loc[idx, "plays"] = plays
        set_df.loc[idx, "wins"] = wins
        set_df.loc[idx, "keys_forged"] = keys_forged
        set_df.loc[idx, "key_diff"] = key_diff
        set_df.loc[idx, "win_rate"] = round(wins / plays * 100, 1)
        set_df.loc[idx, "avg_keys_forged"] = round(keys_forged / plays, 1)
        set_df.loc[idx, "avg_key_diff"] = round(key_diff / plays, 1)

        # Compute average deck performance stats
        set_df.loc[idx, "avg_deck_sas"] = round(np.mean(deck_df.loc[decks_in_set, "SAS"]), 1)
        set_df.loc[idx, "avg_deck_win_rate"] = round(np.mean(deck_df.loc[decks_in_set, "win_rate"]), 1)
        set_df.loc[idx, "std_deck_win_rate"] = round(np.std(deck_df.loc[decks_in_set, "win_rate"]), 1)
    
    return set_df

def set_hms(set_df, deck_df, match_hm):
    """Dataframes with number of plays and number of wins"""

    set_plays_hm = pd.DataFrame(0, index=set_df.index, columns=set_df.index)
    set_wins_hm = pd.DataFrame(0, index=set_df.index, columns=set_df.index)
    for set_1 in set_df.index:
        for set_2 in set_df.index:
            decks_1 = deck_df.index[deck_df["set"] == set_1]
            decks_2 = deck_df.index[deck_df["set"] == set_2]
            plays = (match_hm.loc[decks_1, decks_2] > -1).sum().sum()
            wins = (match_hm.loc[decks_1, decks_2] == 3).sum().sum()
            win_rate = round(wins/plays*100) if plays > 0 else -1
            set_plays_hm.loc[set_1, set_2] = plays
            set_wins_hm.loc[set_1, set_2] = win_rate
    
    return (set_plays_hm, set_wins_hm)


def house_df(deck_df):
    """Dataframe with house statistics"""

    house_df = pd.DataFrame(index=HOUSES.keys())
    for idx in house_df.index:
        # Compute aggregated stats:
        decks_w_house = sum([deck_df[f"house{i}"] == idx for i in [1,2,3]]) == 1
        decks = sum(decks_w_house)
        plays = sum(deck_df.loc[decks_w_house, "plays"])
        wins = sum(deck_df.loc[decks_w_house, "wins"])
        keys_forged = sum(deck_df.loc[decks_w_house, "keys_forged"])
        key_diff = sum(deck_df.loc[decks_w_house, "key_diff"])

        # Add stats to dataframe:
        house_df.loc[idx, "decks"] = decks
        house_df.loc[idx, "plays"] = plays
        house_df.loc[idx, "wins"] = wins
        house_df.loc[idx, "keys_forged"] = keys_forged
        house_df.loc[idx, "key_diff"] = key_diff
        try:
            house_df.loc[idx, "win_rate"] = round(wins / plays * 100, 1)
            house_df.loc[idx, "avg_keys_forged"] = round(keys_forged / plays, 1)
            house_df.loc[idx, "avg_key_diff"] = round(key_diff / plays, 1)
        except ZeroDivisionError:
            pass
        
        # Compute average deck performance stats
        house_df.loc[idx, "avg_deck_sas"] = round(np.mean(deck_df.loc[decks_w_house, "SAS"]), 1)
        house_df.loc[idx, "avg_deck_win_rate"] = round(np.mean(deck_df.loc[decks_w_house, "win_rate"]), 1)
        house_df.loc[idx, "std_deck_win_rate"] = round(np.std(deck_df.loc[decks_w_house, "win_rate"]), 1)

    return house_df


def house_hms(house_df, deck_df, match_hm):
    """Dataframes with number of plays and number of wins"""

    house_plays_hm = pd.DataFrame(0, index=house_df.index, columns=house_df.index)
    house_wins_hm = pd.DataFrame(0, index=house_df.index, columns=house_df.index)
    for house_1 in house_df.index:
        for house_2 in house_df.index:
            decks_1 = deck_df.index[sum([deck_df[f"house{i}"] == house_1 for i in [1,2,3]]) == 1]
            decks_2 = deck_df.index[sum([deck_df[f"house{i}"] == house_2 for i in [1,2,3]]) == 1]
            plays = (match_hm.loc[decks_1, decks_2] > -1).sum().sum()
            wins = (match_hm.loc[decks_1, decks_2] == 3).sum().sum()
            win_rate = round(wins/plays*100) if plays > 0 else -1
            house_plays_hm.loc[house_1, house_2] = plays
            house_wins_hm.loc[house_1, house_2] = win_rate
    
    return (house_plays_hm, house_wins_hm)
