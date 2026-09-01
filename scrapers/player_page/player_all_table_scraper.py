import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.player_page_types import AllStats
from core.browser import start_browser
from core.helper_functions import table_scraper
from core.logger import get_logger

logger = get_logger(__name__)

async def all_stats_scraper(page):
    stats = AllStats()
    try:
        logger.info("Scraping player stats tables")
        await page.select('div[id*="stats_player_summary_"]')
    except Exception as e:
        logger.warning(f"Player stats section could not be loaded: {e}")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    standard_stats_html = soup.select_one('table[id="stats_standard_dom_lg"]')
    shooting_table_html = soup.select_one('table[id="stats_shooting_dom_lg"]')
    playing_time_table_html = soup.select_one('table[id="stats_playing_time_dom_lg"]')
    miscellaneous_stats_table_html = soup.select_one('table[id="stats_misc_dom_lg"]')
    summary_table_html = soup.select_one('table[id*="stats_player_summary_"]')

    try:
        table_scraper(standard_stats_html, "standard_stats", stats)
    except Exception as e:
        logger.warning(f"'standard_stats' table could not be scraped: {e}")

    try:
        table_scraper(shooting_table_html, "shooting_table", stats)
    except Exception as e:
        logger.warning(f"'shooting_table' table could not be scraped: {e}")

    try:
        table_scraper(playing_time_table_html, "playing_time_table", stats)
    except Exception as e:
        logger.warning(f"'playing_time_table' table could not be scraped: {e}")

    try:
        table_scraper(miscellaneous_stats_table_html, "miscellaneous_stats_table", stats)
    except Exception as e:
        logger.warning(f"'miscellaneous_stats_table' table could not be scraped: {e}")

    try:
        table_scraper(summary_table_html, "summary_table", stats)
    except Exception as e:
        logger.warning(f"'summary_table' table could not be scraped: {e}")

    return stats

async def main():
    browser = await start_browser(headless=False)
    try:
        url = "https://fbref.com/en/players/e6af3cc7/Clarence-Seedorf"

        page = await browser.get(url)
        stats = await all_stats_scraper(page)
    finally:
        browser.stop()

if "__main__" == __name__:

    uc.loop().run_until_complete(main())