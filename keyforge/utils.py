
def find_least_played_set_pair(set_plays_hm):
    """Find set pair that has been played the least"""
    for set1, row in (set_plays_hm == set_plays_hm.min().min()).iterrows():
        for set2, val in row.items():
            if val:
                return (set1, set2)


def rank_set_decks_by_plays(deck_df, set_id):
    """Rank sets by usage"""
    set_series = deck_df.loc[deck_df["set"] == set_id, "plays"]
    set_series.sort_values(ascending=True, inplace=True)
    return set_series


def find_next_game(deck_df, match_hm, set_plays_hm):
    """Return next game to play"""
    (set1, set2) = find_least_played_set_pair(set_plays_hm)
    set1_ranked = rank_set_decks_by_plays(deck_df, set1)
    set2_ranked = rank_set_decks_by_plays(deck_df, set2)
    for deck1, _ in set1_ranked.items():
        for deck2, _ in set2_ranked.items():
            if match_hm.loc[deck1, deck2] == -1 and deck1 != deck2:
                return deck_df.loc[[deck1, deck2],]
