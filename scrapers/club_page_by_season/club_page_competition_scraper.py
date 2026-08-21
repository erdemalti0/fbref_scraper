import asyncio
import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.helper_functions import column_name_scraper, table_scraper
from core.club_page_by_season_types import ClubCompetition, CompetitionUrl, ScoringAndFixture


async def competition_scrapper(page, competition_name) -> ClubCompetition | None:
    club = ClubCompetition(
        competition_name=competition_name,
    )

    try:
        print("Turnuva bilgisi alınıyor")
        await page.wait_for('table[id="stats_misc_8"]')
    except Exception as e:
        print(f"Hata {e}")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, 'html.parser')

    scores_and_fixtures_html = soup.select_one('table[id="matchlogs_for"]')
    if scores_and_fixtures_html:
        try:
            table_scraper(scores_and_fixtures_html, "scoring_and_fixture", club, "fixture")
            print(club)
        except Exception as e:
            column_names = None
            print(f"Kolon isimleri alınamadı {e}")

    standard_stats_html = soup.select_one('table[id="stats_standard_8"]')
    if standard_stats_html:
        try:
            table_scraper(standard_stats_html, "standard_stats", club)
        except Exception as e:
            column_names = None
            print(f"Kolon isimleri alınamadı")

    goalkeeping_stats_html = soup.select_one('table[id="stats_keeper_8"]')
    if goalkeeping_stats_html:
        try:
            table_scraper(goalkeeping_stats_html, "goalkeeping_stats", club)
        except Exception as e:
            print(f"Kolon isimleri alınamadı")

    shooting_stats_html = soup.select_one('table[id="stats_shooting_8"]')
    if shooting_stats_html:
        try:
            table_scraper(shooting_stats_html, "shooting_stats", club)
        except Exception as e:
            print(f"Kolon isimleri alınamadı")

    playing_time_stats_html = soup.select_one('table[id="stats_playing_time_8"]')
    if playing_time_stats_html:
        try:
            table_scraper(playing_time_stats_html, "playing_time", club)
        except Exception as e:
            print(f"Kolon isimleri alınamadı")

    miscellaneous_stats_html = soup.select_one('table[id="stats_misc_8"]')
    if miscellaneous_stats_html:
        try:
            table_scraper(miscellaneous_stats_html, "miscellaneous_stats", club)
        except Exception as e:
            print(f"Kolon isimleri alınamadı")

    return club

async def main() -> None:
    browser = await start_browser()
    url = "https://fbref.com/en/squads/18bb7c10/2025-2026/c8/Arsenal-Stats-Champions-League"
    try:
        page = await browser.get(url)
        await asyncio.sleep(3)
        await competition_scrapper(page, "ucl")
    finally:
        browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())