import sys
import asyncio
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.helper_functions import table_scraper, parse_cell_value
from core.league_page_types import LeaguePage, LeaderBoard, LeaderEntry
from core.logger import get_logger

logger = get_logger(__name__)

async def league_leaders_scraper(page, league: LeaguePage):
    logger.info("Scraping league leaders")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    leaders = []
    for div in soup.select('div[id^="leaders_"]'):
        try:
            h4 = div.select_one("h4")
            entries = []
            for entry in div.select("div"):
                if "first_place" in (entry.get("class") or []):
                    continue
                rank_span = entry.select_one('span[class="rank"]')
                who_span = entry.select_one('span[class="who"]')
                value_span = entry.select_one('span[class="value"]')
                if not who_span or not value_span:
                    continue

                player_link = who_span.select_one('a[href*="/players/"]')
                club_span = who_span.select_one('span[class="desc"]')
                rank_text = rank_span.text.strip().replace(".", "") if rank_span else ""

                entries.append(LeaderEntry(
                    rank=int(rank_text) if rank_text.isdigit() else None,
                    player=player_link.text.strip() if player_link else None,
                    club=club_span.text.strip() if club_span else None,
                    value=parse_cell_value(value_span.text.strip()),
                ))

            if entries:
                leaders.append(LeaderBoard(
                    category=div.get("id", "").replace("leaders_", ""),
                    title=h4.text.strip() if h4 else None,
                    entries=entries,
                ))
        except Exception as e:
            logger.warning(f"Leaderboard could not be scraped: {e}")

    if leaders:
        league.leaders = leaders

    nations_html = soup.select_one('table[id="nations"]')
    if nations_html:
        try:
            table_scraper(nations_html, "nations", league)
        except Exception as e:
            logger.warning(f"'nations' table could not be scraped: {e}")

async def main():
    browser = await start_browser()
    try:
        url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        page = await browser.get(url)
        await asyncio.sleep(3)

        league = LeaguePage()
        await league_leaders_scraper(page, league)
        print(league.leaders[0])
    finally:
        browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
