import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.club_page_by_season_types import ClubInfo

async def club_info_scraper(page, url):
    club = ClubInfo()
    try:
        print("Kulüp bilgileri alınıyor")
        await page.wait_for('div[data-template="Partials/Teams/Summary"]')
    except Exception as e:
        raise RuntimeError(f"Kulüp bilgileri alınamadı {e}")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, 'html.parser')

    try:
        club.club_id = url.split("/")[5]
    except Exception as e:
        print(f"match_id alınamadı: {e}")
        club.club_id.match_id = None

    info = soup.select_one('div[data-template="Partials/Teams/Summary"]')
    if info:
        head = info.select_one("h1")
        if head:
            texts = head.text.replace("\n", "").split(' ')
            try:
                club.season = texts[0]
            except Exception as e:
                print(f"Sezon bilgisi alınamadı {e}")

            try:
                club.club_name = texts[1]
            except Exception as e:
                print(f"Kulüp ismi alınamadı {e}")

        paragraphs = info.select('p')
        try:
            for p in paragraphs:
                if p.select_one("strong").text.strip() == "Governing Country:":
                    club.country_name = p.select_one("a").text.strip()
        except Exception as e:
            print(f"Ülke bilgisi alınamadı {e}")
    return club

async def main():
    browser = await start_browser()
    try:
        url = "https://fbref.com/en/squads/18bb7c10/2025-2026/Arsenal-Stats"
        page = await browser.get(url)

        club = await club_info_scraper(page)
        print(club)
    finally:
        browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())