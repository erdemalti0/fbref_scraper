import asyncio
import json
import sys
from pathlib import Path

import nodriver as uc

from scrapers.player_page import player_info_scrapper

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.player_page_types import PlayerPage
from scrapers.player_page.player_info_scrapper import player_info_scraper
from scrapers.player_page.player_all_table_scraper import all_stats_scraper

STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage/players"

async def scrape_page(page, url):

    try:
        await page.wait_for('div[id="footer"]')
    except Exception:
        raise RuntimeError(f"Sayfa tam yüklenemedi {url}")

    player = PlayerPage()

    scrappers = [
        ("info", player_info_scraper(page, url)),
        ("all_stats", all_stats_scraper(page)),
    ]

    for name, coro in scrappers:
        try:
            setattr(player, name, await coro)
        except Exception as e:
            print(f"{name} alınamadı ({url}): {e}")

    return player

def save_report(player: PlayerPage) -> Path | None:
    player_id = player.info.player_id if player.info.player_id else None
    if not player_id:
        print("match_id bulunamadı, rapor kaydedilmedi")
        return None

    STORAGE_DIR.mkdir(exist_ok=True)
    path = STORAGE_DIR / f"{player_id}.json"
    path.write_text(
        json.dumps(player.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Rapor kaydedildi: {path}")
    return path

async def scrape_match_report(url: str, headless: bool = False) -> PlayerPage:
    browser = await start_browser(headless=headless)
    try:
        page = await browser.get(url)
        report = await scrape_page(page, url)
        save_report(report)
        return report
    finally:
        browser.stop()

async def main():
    url = "https://fbref.com/en/players/e6af3cc7/Clarence-Seedorf"
    player = await scrape_match_report(url, headless=False)
    print(player)


if __name__ == "__main__":
    uc.loop().run_until_complete(main())




