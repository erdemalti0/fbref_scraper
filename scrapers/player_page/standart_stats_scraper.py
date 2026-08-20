import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.player_page_types import StandardStats
from core.browser import start_browser

async def standard_stats_scraper(page) -> StandardStats:



async def main():
    browser = await start_browser(headless=False)
    try:
        url = "https://fbref.com/en/players/e6af3cc7/Clarence-Seedorf"

        page = await browser.get(url)
        stats = await standard_stats_scraper(page)
    finally:
        browser.stop()

if "__main__" == __name__:

    uc.loop().run_until_complete(main())