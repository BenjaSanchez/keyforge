import argparse
from html import escape
from string import Template
import warnings
from pathlib import Path

from keyforge import dataframes, plots, utils


warnings.filterwarnings("ignore")

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def render_asset(name, **values):
    """Render a packaged HTML template with the supplied values."""
    template = Template((ASSETS_DIR / name).read_text(encoding="utf-8"))
    return template.substitute(values)


def load_analysis():
    """Load the analysis data and build the figures for the dashboard."""
    data_dir = Path(__file__).resolve().parent.parent / "data"
    deck_path = data_dir / "decks.csv"
    deck_df = dataframes.deck_df(deck_path)
    match_df = dataframes.match_df(data_dir / "matches.csv", deck_path)
    match_hm = dataframes.match_hm(deck_df, match_df)
    dataframes.add_deck_stats(deck_df, match_hm)

    house_df = dataframes.group_df(deck_df, "house")
    house_plays_hm, house_wins_hm = dataframes.group_hms(
        house_df, deck_df, match_hm, "house"
    )
    set_df = dataframes.group_df(deck_df, "set")
    set_plays_hm, set_wins_hm = dataframes.group_hms(
        set_df, deck_df, match_hm, "set"
    )
    figures = [
        ("Deck overview", plots.plot_deck_overview(deck_df)),
        ("Changes over time", plots.plot_time_changes(match_df)),
        ("Deck statistics", plots.plot_deck_stats(deck_df)),
        ("Win rate vs SAS", plots.plot_win_vs_sas(deck_df)),
        (
            "House statistics, plays, and win rates",
            plots.plot_group_heatmaps(house_df, house_plays_hm, house_wins_hm),
        ),
        ("House trends", plots.plot_house_trends(house_df)),
        (
            "Set statistics, plays, and win rates",
            plots.plot_group_heatmaps(set_df, set_plays_hm, set_wins_hm),
        ),
        ("Set trends", plots.plot_set_trends(set_df)),
        ("Match results", plots.plot_match_results(match_hm)),
    ]
    return figures, deck_df, match_df, match_hm, set_plays_hm


def next_game_card(deck_df, match_hm, set_plays_hm):
    """Render the recommended matchup using the dashboard's matchup-card style."""
    next_game = utils.find_next_game(deck_df, match_hm, set_plays_hm)
    cards = []
    for deck_id, deck in next_game.iterrows():
        win_rate = deck["win_rate"]
        win_rate = "—" if win_rate != win_rate else f"{win_rate:.1f}%"
        houses = " / ".join(
            escape(str(deck[f"house{index}"])) for index in range(1, 4)
        )
        cards.append(render_asset(
            "deck_card.html",
            DECK_ID=escape(str(deck_id)),
            DECK_NAME=escape(str(deck["name"])),
            SET=escape(str(deck["set"])),
            HOUSES=houses,
            SAS=escape(str(deck["SAS"])),
            PLAYS=str(int(deck["plays"])),
            WIN_RATE=escape(str(win_rate)),
        ))
    return render_asset(
        "next_match.html",
        DECK_CARDS="\n".join(cards[:1] + ['<div class="versus">VS</div>'] + cards[1:]),
    )


def dataframe_table(title, dataframe):
    table = dataframe.to_html(classes="data-table", border=0, escape=True)
    return render_asset(
        "data_table.html",
        TITLE=escape(title),
        TABLE=table,
    )


def dashboard_page(deck_df, match_df, match_hm, set_plays_hm, charts):
    data_tables = "\n".join(
        [
            dataframe_table("Deck data", deck_df),
            dataframe_table("Match data", match_df),
        ]
    )
    styles = (ASSETS_DIR / "dashboard.css").read_text(encoding="utf-8")
    return render_asset(
        "dashboard.html",
        STYLES=styles,
        NEXT_MATCH=next_game_card(deck_df, match_hm, set_plays_hm),
        CHARTS="\n".join(charts),
        DATA_TABLES=data_tables,
    )


def export_dashboard(output_path):
    """Write all interactive plots to a self-contained HTML page."""
    figures, deck_df, match_df, match_hm, set_plays_hm = load_analysis()
    sections = []
    for index, (title, figure) in enumerate(figures):
        figure.update_layout(autosize=True, width=None)
        plot_html = figure.to_html(
            full_html=False,
            include_plotlyjs=index == 0,
            config={"responsive": True},
            default_width="100%",
        )
        sections.append(render_asset("chart.html", TITLE=escape(title), PLOT=plot_html))

    page = dashboard_page(deck_df, match_df, match_hm, set_plays_hm, sections)
    output_path = Path(output_path)
    output_path.write_text(page, encoding="utf-8")
    return output_path.resolve()


def main():
    parser = argparse.ArgumentParser(
        description="Export the KeyForge plots to an interactive HTML dashboard."
    )
    parser.add_argument(
        "--output",
        default="index.html",
        help="HTML file to write (default: index.html)",
    )
    args = parser.parse_args()
    output_path = export_dashboard(args.output)
    print(f"Dashboard written to {output_path}")


if __name__ == "__main__":
    main()
