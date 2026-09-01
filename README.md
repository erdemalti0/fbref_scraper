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
git clone https://github.com/erdemalti0/fbref_scrapper
cd fbref_scrapper
uv sync
```

Chrome must be installed on your machine (nodriver drives a real Chrome instance — headless mode does not work, fbref blocks headless browsers).

## Usage

```bash
python main.py <type> <url>
```

| Type     | Description        | Example URL                                                            |
|----------|--------------------|------------------------------------------------------------------------|
| `match`  | Match report       | `https://fbref.com/en/matches/675b328b/...`                            |
| `player` | Player page        | `https://fbref.com/en/players/e6af3cc7/Clarence-Seedorf`               |
| `club`   | Club season page   | `https://fbref.com/en/squads/.../Galatasaray-Stats`                    |
| `league` | League page        | `https://fbref.com/en/comps/9/Premier-League-Stats`                    |

Example:

```bash
python main.py league https://fbref.com/en/comps/9/Premier-League-Stats
```

If the URL does not match the type (e.g. a player URL with the `match` type), the program exits with an error before opening the browser. For details:

```bash
python main.py --help
```

## Output

Scraped data is saved as JSON under `storage/`:

```
storage/
├── players/    # player reports
├── clubs/      # club reports
├── leagues/    # league/tournament reports
└── *.json      # match reports
```

File names come from the IDs on the page (e.g. `9_2026-2027.json` for the 2026-2027 Premier League season).

Logs are written to `logs/scraper.log` with rotation, and also printed to the console.

## Project Structure

```
core/                       # browser, type definitions (pydantic), helper functions, storage, logger
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

## License

MIT
