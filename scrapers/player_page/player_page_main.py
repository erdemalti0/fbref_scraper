import sys
import asyncio
from pathlib import Path

import nodriver as uc

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.storage import save_json
from core.player_page_types import PlayerPage
from core.logger import get_logger
from scrapers.player_page.player_info_scraper import player_info_scraper
from scrapers.player_page.player_all_table_scraper import all_stats_scraper

logger = get_logger(__name__)

STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage/players"

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

    player = PlayerPage()

    scrappers = [
        ("info", player_info_scraper(page, url)),
        ("all_stats", all_stats_scraper(page)),
    ]

    for name, coro in scrappers:
        try:
            setattr(player, name, await coro)
        except Exception as e:
            logger.error(f"Section '{name}' could not be scraped ({url}): {e}")

    return player

def save_report(player: PlayerPage) -> Path | None:
    player_id = player.info.player_id if player.info and player.info.player_id else None
    return save_json(player, STORAGE_DIR, player_id, "player")

async def scrape_player_page(url: str) -> PlayerPage:
    browser = await start_browser()
    try:
        page = await browser.get(url)
        report = await scrape_page(page, url)
        save_report(report)
        return report
    finally:
        browser.stop()

async def main():
    url = "https://fbref.com/en/players/e6af3cc7/Clarence-Seedorf"
    player = await scrape_player_page(url)
    print(player)


if __name__ == "__main__":
    uc.loop().run_until_complete(main())




