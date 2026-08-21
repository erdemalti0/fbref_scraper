import sys

from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.match_report_types import PlayerStats, MatchPlayerStats
from core.browser import start_browser
from core.helper_functions import column_name_scraper, row_scraper, column_description_mapper


async def player_stats_scraper(page):

    match_player_stats = MatchPlayerStats()

    try:
        print("Scraping player stats")
        await page.select('table[class="stats_table sortable now_sortable"]')
    except Exception as e:
        raise RuntimeError(f"Oyuncu istatistik tablosu alınamadı {e}")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    tables = soup.select('table[class="stats_table sortable now_sortable"]')
    goalkeeper_tables = soup.select('table[id*="keeper_stats"]')
    if tables and len(tables) > 1:
        home_table = tables[0]
        away_table = tables[1]

        tr_in_col_names = home_table.select_one("thead").select("tr")[1]

        if tr_in_col_names:
            column_names = column_name_scraper(tr_in_col_names)

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

        tr_in_col_names = home_goalkeeper_table.select_one("thead").select("tr")[1]

        if tr_in_col_names:
            column_names = column_name_scraper(tr_in_col_names)
            match_player_stats.goalkeeper_column_descriptions = column_description_mapper(column_names)
            try:
                home_rows = home_goalkeeper_table.select_one("tbody").select('tr')
                away_rows = away_goalkeeper_table.select_one("tbody").select("tr")

                match_player_stats.home_goalkeeper_stats = row_scraper(home_rows, column_names)
                match_player_stats.away_goalkeeper_stats = row_scraper(away_rows, column_names)
            except Exception as e:
                print(e)
        else:
            print("Kalece tabloları alınamadı")


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