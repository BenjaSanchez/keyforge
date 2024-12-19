from keyforge import dataframes, plots, utils
import warnings
warnings.filterwarnings("ignore")


# Load decks:
deck_df = dataframes.deck_df()
print(deck_df)
f = plots.plot_deck_overview(deck_df)

# Load matches:
match_df = dataframes.match_df()
print(match_df)
plots.plot_time_changes(match_df)
match_hm = dataframes.match_hm(deck_df, match_df)
plots.plot_match_results(match_hm)

# Deck stats:
dataframes.add_deck_stats(deck_df, match_hm)
plots.plot_deck_stats(deck_df)
plots.plot_win_vs_sas(deck_df)

# House stats:
house_df = dataframes.group_df(deck_df, "house")
(house_plays_hm, house_wins_hm) = dataframes.group_hms(house_df, deck_df, match_hm, "house")
plots.plot_group_heatmaps(house_df, house_plays_hm, house_wins_hm, 22)
plots.plot_house_trends(house_df)

# Set stats:
set_df = dataframes.group_df(deck_df, "set")
(set_plays_hm, set_wins_hm) = dataframes.group_hms(set_df, deck_df, match_hm, "set")
plots.plot_group_heatmaps(set_df, set_plays_hm, set_wins_hm, 18)
plots.plot_set_trends(set_df)
utils.find_next_game(deck_df, match_hm, set_plays_hm)
