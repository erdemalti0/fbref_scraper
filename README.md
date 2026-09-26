# FBRef Scraper

A web scraper for collecting football data from [fbref.com](https://fbref.com). It opens pages in a real Chrome browser, parses the tables, and saves the results as JSON.

## What Can Be Scraped?

The project supports 4 page types:

### Match Report (`match`)
Detailed report of a single match:
- General match info (date, stadium, referee, score)
- Team stats (shots, shots on target, saves, possession, etc.)
- Player stats (all players from both teams)
- Match events (goals, assists, cards, substitutions)
- Squads and formations

### Player Page (`player`)
A player's profile page:
- Player info (name, position, height, weight, foot, birth date, etc.)
- Career stat tables (standard, shooting, passing, defense, and all other tables)

### Club Page (`club`)
A club's season page:
- Club info
- Stat tables for every competition the club played that season (league, cup, european competitions, etc.)

### League / Tournament Page (`league`)
A league or tournament page (including the Champions League):
- League info
- Standings (including group tables in tournaments like the UCL, multi-table support)
- Squad stats (for/against)
- Fixtures and links to played matches
- Leaderboards (top scorer, top assists, etc. — 35 categories)
- Nation distribution

## Installation

The project is managed with [uv](https://docs.astral.sh/uv/). Requires Python 3.11+.

```bash
git clone https://github.com/erdemalti0/fbref_scraper
cd fbref_scraper
uv sync
```

Chrome must be installed on your machine (nodriver drives a real Chrome instance — headed mode (`HEADLESS=False`, the default) is recommended, fbref may block headless browsers).

## Usage

```bash
python main.py <type> <url> [--headless true|false] [--storage_type json|postgresql|both]
```

- `--headless`: run Chrome headless (`true`/`false`). If omitted, the `HEADLESS` value from `.env` (`.env.local` overrides `.env`) is used; default is `False` (headed). Note: fbref may block headless browsers, so headed mode is recommended.
- `--storage_type`: where to save the result — `json`, `postgresql`, or `both`. If omitted, the `STORAGE_TYPE` value from `.env` is used; default is `json`.

| Type     | Description        | Example URL                                                            |
|----------|--------------------|------------------------------------------------------------------------|
| `match`  | Match report       | `https://fbref.com/en/matches/675b328b/...`                            |
| `player` | Player page        | `https://fbref.com/en/players/e6af3cc7/Clarence-Seedorf`               |
| `club`   | Club season page   | `https://fbref.com/en/squads/206d90db/Barcelona-Stats`                 |
| `league` | League page        | `https://fbref.com/en/comps/9/Premier-League-Stats`                    |

Example:

```bash
python main.py league https://fbref.com/en/comps/9/Premier-League-Stats
python main.py match https://fbref.com/en/matches/675b328b/... --storage_type both
```

## Configuration (`.env`)

| Variable             | Description                                                        | Default |
|----------------------|--------------------------------------------------------------------|---------|
| `HEADLESS`           | Run Chrome headless (`True`/`False`)                               | `False` |
| `STORAGE_TYPE`       | Where to save results: `json`, `postgresql`, or `both`             | `json`  |
| `DB_CONNECTION_STRING` | PostgreSQL connection string, e.g. `postgresql://user:pass@localhost:5432/fbref` | _(empty)_ |

`.env.local` overrides `.env` when both exist. CLI flags (`--headless`, `--storage_type`) override both.

If the URL does not match the type (e.g. a player URL with the `match` type), the program exits with an error before opening the browser. For details:

```bash
python main.py --help
```

## Output

### JSON

Scraped data is saved as JSON under `storage/`:

```
storage/
├── players/    # player reports
├── clubs/      # club reports
├── leagues/    # league/tournament reports
└── *.json      # match reports
```

File names come from the IDs on the page (e.g. `9_2026-2027.json` for the 2026-2027 Premier League season).

### PostgreSQL

With `--storage_type postgresql` (or `both`), the report is also upserted into PostgreSQL (keyed on `report_id`, so re-scraping the same page updates the row instead of duplicating it). Tables are created automatically if missing:

| Scraper  | Table           |
|----------|-----------------|
| `match`  | `match_reports` |
| `player` | `players`       |
| `club`   | `clubs`         |
| `league` | `leagues`       |

Schema (same for all tables):

| Column     | Type                       | Notes                        |
|------------|----------------------------|------------------------------|
| `id`       | `INTEGER` (PK)             | Auto-increment               |
| `report_id`| `TEXT UNIQUE NOT NULL`     | Page ID (e.g. match ID)      |
| `created_at` | `TIMESTAMPTZ`            | Defaults to `now()`          |
| `data`     | `JSONB NOT NULL`           | Full scraped report          |

### Querying PostgreSQL (JSONB examples)

The whole report lives in the `data` column. Use `->` (returns JSONB) and `->>` (returns text) to navigate it:

```sql
-- All matches with scores
SELECT
  report_id,
  data -> 'general_info' ->> 'home_name' AS home,
  (data -> 'general_info' ->> 'home_goals')::int AS home_goals,
  (data -> 'general_info' ->> 'away_goals')::int AS away_goals,
  data -> 'general_info' ->> 'away_name' AS away
FROM match_reports;
```

```sql
-- Home goal scorers of one match (one row per scorer)
SELECT
  scorer ->> 'scorer' AS scorer,
  scorer ->> 'minute' AS minute
FROM match_reports,
     jsonb_array_elements(data -> 'general_info' -> 'home_goal_scorers') AS scorer
WHERE report_id = '675b328b';
```

```sql
-- Matches where a team had more than 60% possession
SELECT
  report_id,
  data -> 'general_info' ->> 'home_name' AS home,
  (data -> 'team_stats' ->> 'home_possession')::float AS home_possession
FROM match_reports
WHERE (data -> 'team_stats' ->> 'home_possession')::float > 60
   OR (data -> 'team_stats' ->> 'away_possession')::float > 60;
```

```sql
-- Players by position
SELECT
  report_id,
  data -> 'info' ->> 'player_name' AS player,
  data -> 'info' ->> 'player_position' AS position
FROM players
WHERE data -> 'info' ->> 'player_position' = 'Midfielder';
```

```sql
-- League standings (one row per team)
SELECT
  report_id,
  row ->> 'squad' AS team,
  (row ->> 'pts')::int AS points
FROM leagues,
     jsonb_array_elements(data -> 'standings' -> 0 -> 'rows') AS row
WHERE data -> 'league_info' ->> 'comp_id' = '9'
ORDER BY points DESC;
```

Tip: for frequent filters, add a GIN index — `CREATE INDEX ON match_reports USING gin (data);` — or an expression index on the exact path you query, e.g. `CREATE INDEX ON match_reports (((data -> 'general_info') ->> 'league'));`

Logs are written to `logs/scraper.log` with rotation, and also printed to the console.

## Project Structure

```
core/                       # browser, helper functions, storage, logger
models/                     # pydantic data models
scrapers/
├── match_report/           # match report scrapers
├── player_page/            # player page scrapers
├── club_page_by_season/    # club page scrapers
└── league_page/            # league/tournament scrapers
main.py                     # CLI entry point
```

Each scraper module can be tested independently via its own `if __name__ == "__main__"` block.

## Technologies

- **nodriver** — Chrome-based browser automation
- **BeautifulSoup** — HTML parsing
- **pydantic** — data models and JSON serialization
- **SQLAlchemy** + **psycopg** — PostgreSQL storage (JSONB)

## License

MIT
