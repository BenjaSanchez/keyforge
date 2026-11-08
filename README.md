# KeyForge Stats

An interactive dashboard for exploring my KeyForge deck and match data. It includes deck overviews and statistics, trends over time, win rates by SAS, house and set heatmaps, match results, and a suggested next matchup. The dashboard is generated from `data/decks.csv` and `data/matches.csv` and written as a self-contained HTML file.

## Generate the dashboard

From the repository root, create and activate a Conda environment:

```shell
conda create -n keyforge python=3.12
conda activate keyforge
```

Install the project and its dependencies, then generate the dashboard:

```shell
python -m pip install -e .
keyforge-dashboard
```

This writes `index.html` in the current directory. To choose another output path, pass `--output`:

```shell
keyforge-dashboard --output build/index.html
```

Open the generated HTML file in a browser to explore the charts and data tables.

## Publish with GitHub Pages

The GitHub Actions workflow in `.github/workflows/publish-dashboard.yml` generates the dashboard on each push to `main` and publishes it to the root of the `gh-pages` branch. It can also be run manually from the repository's **Actions** tab.

To serve the published dashboard, go to **Settings → Pages**, choose **Deploy from a branch**, select `gh-pages` and `/(root)`, and save. Once the workflow has completed and Pages is enabled, the site is available at <https://benjasanchez.github.io/keyforge/>.
