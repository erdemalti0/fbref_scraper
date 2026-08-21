import asyncio
import json
import sys
from pathlib import Path

import nodriver as uc

from core.club_page_by_season_types import ClubPageBySeason
from scrapers.player_page import player_info_scrapper

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from scrapers.club_page_by_season.club_info_scraper import club_info_scraper
from scrapers.club_page_by_season.club_page_competition_url_scraper import competition_url_scraper
from scrapers.club_page_by_season.club_page_competition_scraper import competition_scrapper

STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage/clubs"


async def scrape_page(page, url, browser):

    try:
        await page.wait_for('div[id="footer"]')
    except Exception:
        raise RuntimeError(f"Sayfa tam yüklenemedi {url}")

    club = ClubPageBySeason()

    urls = await competition_url_scraper(page, url)
    competitions = []
    if urls:
        for u in urls:
            try:
                new_page = await browser.get(u.competition_url)
                competition = await competition_scrapper(new_page, u.competition_name)
                competitions.append(competition)
            except Exception as e:
                print(f"Turnuva bilgisi alınamadı")

            await asyncio.sleep(3)

    if competitions:
        club.competitions = competitions

    try:
        info = await club_info_scraper(page, url)
        if info:
            club.club_info = info
    except Exception as e:
        print(f"Club info alınamadı {e}")


    return club

def save_report(club: ClubPageBySeason) -> Path | None:
    club_id = club.club_info.club_id if club.club_info.club_id else None
    if not club_id:
        print("club_id bulunamadı, rapor kaydedilmedi")
        return None

    STORAGE_DIR.mkdir(exist_ok=True)
    path = STORAGE_DIR / f"{club_id}.json"
    path.write_text(
        json.dumps(club.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Rapor kaydedildi: {path}")
    return path

async def scrape_club_page(url: str, headless: bool = False) -> ClubPageBySeason:
    browser = await start_browser(headless=headless)
    try:
        page = await browser.get(url)
        club = await scrape_page(page, url, browser)
        save_report(club)
        return club
    finally:
        browser.stop()

async def main():
    url = "https://fbref.com/en/squads/18bb7c10/2025-2026/Arsenal-Stats"
    club = await scrape_club_page(url, headless=False)

if __name__ == "__main__":
    uc.loop().run_until_complete(main())