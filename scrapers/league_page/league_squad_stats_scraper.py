import sys
import asyncio
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.helper_functions import table_scraper
from core.league_page_types import LeaguePage
from core.logger import get_logger

logger = get_logger(__name__)

async def league_squad_stats_scraper(page, league: LeaguePage):
    logger.info("Scraping squad stats")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    for stat_type in ["standard", "keeper", "shooting", "playing_time", "misc"]:
        for side in ["for", "against"]:
            table_html = soup.select_one(f'table[id="stats_squads_{stat_type}_{side}"]')
            if table_html:
                try:
                    table_scraper(table_html, f"squad_{stat_type}_{side}", league)
                except Exception as e:
                    logger.warning(f"'squad_{stat_type}_{side}' table could not be scraped: {e}")

async def main():
    browser = await start_browser()
    try:
        url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        page = await browser.get(url)
        await asyncio.sleep(3)

        league = LeaguePage()
        await league_squad_stats_scraper(page, league)
        print(league)
    finally:
        browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
