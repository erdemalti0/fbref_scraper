import sys
import re
import asyncio
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.helper_functions import column_name_scraper, row_scraper
from core.league_page_types import TableRow
from core.logger import get_logger

logger = get_logger(__name__)

async def league_fixture_scraper(page, comp_id, season=None):
    logger.info("Scraping league fixtures")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    sched_link = None
    if season:
        sched_link = soup.select_one(f'a[href*="/comps/{comp_id}/{season}/schedule/"]')
    if not sched_link:
        sched_link = soup.select_one(f'a[href*="/comps/{comp_id}/schedule/"]')
    if not sched_link:
        logger.warning("Schedule link not found on league page")
        return None, None

    schedule_url = sched_link.get("href").strip()
    if not schedule_url.startswith("https://fbref.com"):
        schedule_url = "https://fbref.com" + schedule_url

    await page.get(schedule_url)
    await asyncio.sleep(3)

    soup = BeautifulSoup(await page.get_content(), "html.parser")

    if season:
        h1 = soup.select_one("h1")
        if h1 and season not in h1.text:
            logger.warning(f"Schedule page season mismatch: expected {season}, got '{h1.text.strip()}'")
            return None, None

    table = soup.select_one('table[id^="sched"]')
    if not table:
        logger.warning("Schedule table not found")
        return None, None

    fixtures = None
    try:
        thead_rows = table.select_one("thead").select("tr")
        column_names = column_name_scraper(thead_rows[-1])
        rows = table.select_one("tbody").select("tr")
        fixtures = row_scraper(rows, column_names, TableRow)
    except Exception as e:
        logger.warning(f"League fixtures could not be parsed: {e}")

    match_urls = []
    for tr in table.select_one("tbody").select("tr"):
        for a in tr.select('a[href*="/matches/"]'):
            href = (a.get("href") or "").strip()
            if not re.search(r"/matches/[0-9a-f]{8}", href):
                continue
            if not href.startswith("https://fbref.com"):
                href = "https://fbref.com" + href
            if href not in match_urls:
                match_urls.append(href)

    return fixtures, match_urls

async def main():
    browser = await start_browser()
    try:
        url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        page = await browser.get(url)
        await asyncio.sleep(3)

        fixtures, match_urls = await league_fixture_scraper(page, "9", "2026-2027")
        print(len(fixtures), len(match_urls))
    finally:
        browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
