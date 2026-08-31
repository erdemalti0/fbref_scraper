import asyncio
import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.helper_functions import column_name_scraper, table_scraper
from core.club_page_by_season_types import ClubCompetition


def comp_matches(row_comp, competition_name) -> bool:
    row = str(row_comp).strip().lower()
    comp = competition_name.strip().lower()
    return comp in row or row in comp


async def competition_scraper(page, competition_name) -> ClubCompetition | None:
    club = ClubCompetition(
        competition_name=competition_name,
    )

    try:
        print("Turnuva bilgisi alınıyor")
        await page.wait_for('table[id*="stats_misc_"]')
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

    if club.scoring_and_fixture and competition_name != "All Competitions":
        filtered_rows = [
            row for row in club.scoring_and_fixture
            if getattr(row, "comp", None) is None or comp_matches(row.comp, competition_name)
        ]
        if filtered_rows:
            club.scoring_and_fixture = filtered_rows

    standard_stats_html = soup.select_one('table[id*="stats_standard_"]')
    if standard_stats_html:
        try:
            table_scraper(standard_stats_html, "standard_stats", club)
        except Exception as e:
            column_names = None
            print(f"Kolon isimleri alınamadı")

    goalkeeping_stats_html = soup.select_one('table[id*="stats_keeper_"]')
    if goalkeeping_stats_html:
        try:
            table_scraper(goalkeeping_stats_html, "goalkeeping_stats", club)
        except Exception as e:
            print(f"Kolon isimleri alınamadı")

    shooting_stats_html = soup.select_one('table[id*="stats_shooting_"]')
    if shooting_stats_html:
        try:
            table_scraper(shooting_stats_html, "shooting_stats", club)
        except Exception as e:
            print(f"Kolon isimleri alınamadı")

    playing_time_stats_html = soup.select_one('table[id*="stats_playing_time_"]')
    if playing_time_stats_html:
        try:
            table_scraper(playing_time_stats_html, "playing_time", club)
        except Exception as e:
            print(f"Kolon isimleri alınamadı")

    miscellaneous_stats_html = soup.select_one('table[id*="stats_misc_"]')
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
        await competition_scraper(page, "ucl")
    finally:
        browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())