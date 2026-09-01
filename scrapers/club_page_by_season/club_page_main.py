import asyncio
import sys
from pathlib import Path

import nodriver as uc

from core.club_page_by_season_types import ClubPageBySeason

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.storage import save_json
from scrapers.club_page_by_season.club_info_scraper import club_info_scraper
from scrapers.club_page_by_season.club_page_competition_url_scraper import competition_url_scraper
from scrapers.club_page_by_season.club_page_competition_scraper import competition_scraper

STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage/clubs"


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
        raise RuntimeError(f"Sayfa tam yüklenemedi {url}")

    club = ClubPageBySeason()

    urls = await competition_url_scraper(page, url)
    competitions = []
    if urls:
        for u in urls:
            try:
                if u.competition_url:
                    await page.get(u.competition_url)
                    await asyncio.sleep(3)
                competition = await competition_scraper(page, u.competition_name)
                competitions.append(competition)
            except Exception as e:
                print(f"Turnuva bilgisi alınamadı {e}")

    if competitions:
        club.competitions = competitions

    try:
        await page.get(url)
        info = await club_info_scraper(page, url)
        if info:
            club.club_info = info
    except Exception as e:
        print(f"Club info alınamadı {e}")


    return club

def save_report(club: ClubPageBySeason) -> Path | None:
    club_id = club.club_info.club_id if club.club_info and club.club_info.club_id else None
    return save_json(club, STORAGE_DIR, club_id, "club")

async def scrape_club_page(url: str) -> ClubPageBySeason:
    browser = await start_browser()
    try:
        page = await browser.get(url)
        club = await scrape_page(page, url)
        save_report(club)
        return club
    finally:
        browser.stop()

async def main():
    url = "https://fbref.com/en/squads/18bb7c10/2025-2026/Arsenal-Stats"
    club = await scrape_club_page(url)

if __name__ == "__main__":
    uc.loop().run_until_complete(main())