# Deutsche Bahn Statistics

Deutsche Bahn Statistics is a (German) [website](https://piebro.github.io/deutsche-bahn-statistics/questions) with plots and tables about the Deutsche Bahn together with Python code to create them.
The statistics are automatically updated monthly and use publicly available data.
The data is available in a separate repo here: [https://github.com/piebro/deutsche-bahn-data](https://github.com/piebro/deutsche-bahn-data).

## Develop

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/piebro/deutsche-bahn-statistics
   cd deutsche-bahn-data
   ```

2. Install the required dependencies in a virtual environment using [uv](https://docs.astral.sh/uv/getting-started/installation/):
   ```bash
   uv sync
   ```

3. Download the data files:
   ```bash
   bash download_data.sh
   ```

4. Host the website locally:
   ```bash
   uv run -m http.server
   ```

### Update Statistics Manually

```bash
uv run run_all_calculations.py
```

### Add a new Question

Do it manually and copy the folder structure of the previous question.
An overview of the dataset with its columns can be found in the [data repository](https://github.com/piebro/deutsche-bahn-data).

Update all the generated parts of index.html using the following script, after adding a new question.
```bash
START_DATE=$(date -d "$(date +%Y-%m-01) -3 month" +%Y.%m.%d)
END_DATE=$(date +%Y.%m.01)
uv run generate_html_links.py $START_DATE $END_DATE "allgemein,zeitraum,direkter_zug,zugverbindung,verspaetungsverlauf_zugfahrt,verspaetung_pro_bahnhof,zuggattungen_pro_bahnhof,bahnhof,zuggattung"
```

Use `ruff check` and `ruff format` to lint and format the Python code before committing new code.

## Related Deutsche Bahn and Open Data Websites

There are a few other projects that look at similar data.
- [Video](https://www.youtube.com/watch?v=0rb9CfOvojk): BahnMining - Pünktlichkeit ist eine Zier (David Kriesel) [2019]
- [www.deutschebahn.com](https://www.deutschebahn.com/de/konzern/konzernprofil/zahlen_fakten/puenktlichkeitswerte-6878476#): official statistics from Deutsche Bahn
- [bahn.expert](https://bahn.expert): look at the departure monitor of train stations in real time
- [next.bahnvorhersage.de](https://next.bahnvorhersage.de): a tool to calculate the probability that a train connection works using historical data
- [www.zugfinder.net](https://www.zugfinder.net/de/start): multiple maps of current train positions and statistics for long-distance trains in Germany, Austria, BeNeLux, Denmark, Italy and Slovenia
- [strecken-info.de](https://strecken-info.de/): a map of the German railroads with current construction sites and disruptions on the routes
- [openrailwaymap.org](https://openrailwaymap.org/): a worldwide map with railway infrastructure using OpenStreetMap Data
- [zugspaet.de](https://zugspaet.de): a website, where you can then enter your train and see how often it was late or on time in the past

## Contributing

Contributions are welcome. Open an Issue if you want to report a bug, have an idea, or want to propose a change.

## Website Statistics

There is lightweight tracking with [Plausible](https://plausible.io/about) for the [website](https://piebro.github.io/deutsche-bahn-statistics/) to get info about how many people are visiting.
Everyone who is interested can look at these stats here: https://plausible.io/piebro.github.io%2Fdeutsche-bahn-statistics?period=30d.
Only users without an AdBlocker are counted, so these statistics are underestimating the actual count of visitors.
I would guess that quite a few people (including me) visiting the site have an AdBlocker.

## License

All code in this project is licensed under the MIT License.
The [data](https://developers.deutschebahn.com/db-api-marketplace/apis/product/timetables) is licensed under [Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) by Deutsche Bahn.
