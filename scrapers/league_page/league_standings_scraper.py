import sys
import re
import asyncio
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.helper_functions import column_name_scraper, row_scraper, column_description_mapper
from core.league_page_types import StandingsTable, TableRow
from core.logger import get_logger

logger = get_logger(__name__)

async def league_standings_scraper(page):
    logger.info("Scraping standings")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    standings = []
    tables = soup.select('table[id^="results"][id$="_overall"]')
    if not tables:
        logger.warning("No standings tables found")

    for table in tables:
        try:
            wrapper = table.find_parent("div", id=lambda v: v and v.startswith("all_results"))
            h2 = wrapper.select_one("h2") if wrapper else None
            group_match = re.search(r"([A-Z])_overall$", table.get("id") or "")
            if h2:
                phase = h2.text.strip()
            elif group_match:
                phase = f"Group {group_match.group(1)}"
            else:
                phase = table.get("id")

            thead_rows = table.select_one("thead").select("tr")
            column_names = column_name_scraper(thead_rows[-1])
            rows = table.select_one("tbody").select("tr")
            table_rows = row_scraper(rows, column_names, TableRow)

            if table_rows:
                standings.append(StandingsTable(
                    phase=phase,
                    column_descriptions=column_description_mapper(column_names),
                    rows=table_rows,
                ))
        except Exception as e:
            logger.warning(f"Standings table could not be scraped: {e}")

    home_away = None
    home_away_table = soup.select_one('table[id^="results"][id$="_home_away"]')
    if home_away_table:
        try:
            thead_rows = home_away_table.select_one("thead").select("tr")
            column_names = column_name_scraper(thead_rows[-1])
            rows = home_away_table.select_one("tbody").select("tr")
            home_away = row_scraper(rows, column_names, TableRow)
        except Exception as e:
            logger.warning(f"Home/away standings could not be scraped: {e}")

    return standings if standings else None, home_away

async def main():
    browser = await start_browser()
    try:
        url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        page = await browser.get(url)
        await asyncio.sleep(3)

        standings, home_away = await league_standings_scraper(page)
        print(standings)
    finally:
        browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
