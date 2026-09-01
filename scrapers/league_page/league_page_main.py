import asyncio
import sys
from pathlib import Path

import nodriver as uc

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.storage import save_json
from core.league_page_types import LeaguePage
from core.logger import get_logger
from scrapers.league_page.league_info_scraper import league_info_scraper
from scrapers.league_page.league_standings_scraper import league_standings_scraper
from scrapers.league_page.league_squad_stats_scraper import league_squad_stats_scraper
from scrapers.league_page.league_fixture_scraper import league_fixture_scraper
from scrapers.league_page.league_leaders_scraper import league_leaders_scraper

logger = get_logger(__name__)

STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage/leagues"


async def scrape_page(page, url):

    loaded = False
    for attempt in range(3):
        try:
            await page.wait_for('div[id="footer"]')
            loaded = True
            break
        except Exception:
            await asyncio.sleep(2)
    if not loaded:
        raise RuntimeError(f"Page did not fully load {url}")

    league = LeaguePage()

    try:
        league.league_info = await league_info_scraper(page, url)
    except Exception as e:
        logger.error(f"League info could not be scraped ({url}): {e}")

    try:
        league.standings, league.standings_home_away = await league_standings_scraper(page)
    except Exception as e:
        logger.error(f"Standings could not be scraped ({url}): {e}")

    try:
        await league_squad_stats_scraper(page, league)
    except Exception as e:
        logger.error(f"Squad stats could not be scraped ({url}): {e}")

    try:
        await league_leaders_scraper(page, league)
    except Exception as e:
        logger.error(f"Leaders could not be scraped ({url}): {e}")

    try:
        comp_id = league.league_info.comp_id if league.league_info else None
        season = league.league_info.season if league.league_info else None
        league.fixtures, league.match_urls = await league_fixture_scraper(page, comp_id, season)
    except Exception as e:
        logger.error(f"Fixtures could not be scraped ({url}): {e}")

    return league

def save_report(league: LeaguePage) -> Path | None:
    comp_id = league.league_info.comp_id if league.league_info and league.league_info.comp_id else None
    season = league.league_info.season if league.league_info and league.league_info.season else None
    report_id = f"{comp_id}_{season}" if comp_id and season else comp_id
    return save_json(league, STORAGE_DIR, report_id, "league")

async def scrape_league_page(url: str) -> LeaguePage:
    browser = await start_browser()
    try:
        page = await browser.get(url)
        league = await scrape_page(page, url)
        save_report(league)
        return league
    finally:
        browser.stop()

async def main():
    url = "https://fbref.com/en/comps/9/Premier-League-Stats"
    league = await scrape_league_page(url)

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
