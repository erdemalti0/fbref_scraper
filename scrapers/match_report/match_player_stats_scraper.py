import sys

from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path
import re

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.match_report_types import PlayerStats, MatchPlayerStats
from core.browser import start_browser

def column_name_scraper(content) -> list:

    names = []
    try:
        for column in content.select('th[class*="poptip"]'):
            col_name = column.text.strip()
            col_description = None

            try:
                data_tip_content = column.get("data-tip", "")
                match = re.search(r"<strong>(.*?)</strong>", data_tip_content)
                column_description = match.group(1).strip() if match else None

                col_description = column_description
            except Exception as e:
                print(f"Column description error: {e}")

            col_obj = {
                "column_name": col_name,
                "column_description": col_description,
            }

            names.append(col_obj)

    except Exception as e:
        print(f"Kolon isimleri alınamadı")

    return names

def parse_cell_value(text: str):
    """Boş hücre None, sayısal değerler int/float olarak döner."""
    if not text:
        return None
    if text.isdigit():
        return int(text)
    try:
        return float(text)
    except ValueError:
        return text

def column_description_mapper(columns) -> dict[str, str]:
    return {
        col["column_name"].strip().lower(): col["column_description"]
        for col in columns
        if col["column_name"].strip() and col["column_description"]
    }

def row_scraper(content, columns) -> list[PlayerStats]:

    result = []
    for row in content:
        stats = PlayerStats()
        all_cels = row.find_all(["th", "td"])
        for i, cel in enumerate(all_cels):
            var_name = columns[i]["column_name"].strip().lower()
            if var_name:
                setattr(stats, var_name, parse_cell_value(cel.text.strip()))

        result.append(stats)

    return result

async def player_stats_scraper(page):

    match_player_stats = MatchPlayerStats()

    try:
        print("Scraping player stats")
        await page.select('table[class="stats_table sortable now_sortable"')
    except Exception as e:
        raise RuntimeError(f"Oyuncu istatistik tablosu alınamadı {e}")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    tables = soup.select('table[class="stats_table sortable now_sortable"]')
    goalkeeper_tables = soup.select('table[id*="keeper_stats"]')
    if tables and len(tables) > 1:
        home_table = tables[0]
        away_table = tables[1]

        column_names = column_name_scraper(home_table)
        match_player_stats.column_descriptions = column_description_mapper(column_names)
        try:
            home_rows = home_table.select_one("tbody").select('tr')
            away_rows = away_table.select_one("tbody").select("tr")

            match_player_stats.home_stats = row_scraper(home_rows, column_names)
            match_player_stats.away_stats = row_scraper(away_rows, column_names)
        except Exception as e:
            print(e)


    if goalkeeper_tables:
        home_goalkeeper_table = goalkeeper_tables[0]
        away_goalkeeper_table = goalkeeper_tables[1]

        column_names = column_name_scraper(home_goalkeeper_table)
        match_player_stats.goalkeeper_column_descriptions = column_description_mapper(column_names)
        try:
            home_rows = home_goalkeeper_table.select_one("tbody").select('tr')
            away_rows = away_goalkeeper_table.select_one("tbody").select("tr")

            match_player_stats.home_goalkeeper_stats = row_scraper(home_rows, column_names)
            match_player_stats.away_goalkeeper_stats = row_scraper(away_rows, column_names)
        except Exception as e:
            print(e)


    return match_player_stats



async def main():
    browser = await start_browser(headless=False)
    try:
        url = "https://fbref.com/en/matches/91a56b43/Genclerbirligi-Fenerbahce-August-15-2026-Super-Lig"

        page = await browser.get(url)
        stats = await player_stats_scraper(page)
    finally:
        browser.stop()

if "__main__" == __name__:

    uc.loop().run_until_complete(main())