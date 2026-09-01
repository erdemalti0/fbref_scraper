import sys
import re
import asyncio
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.club_page_by_season_types import ClubInfo

async def club_info_scraper(page, url):
    club = ClubInfo()
    print("Kulüp bilgileri alınıyor")
    loaded = False
    for attempt in range(3):
        try:
            await page.wait_for('div[data-template="Partials/Teams/Summary"]')
            loaded = True
            break
        except Exception:
            await asyncio.sleep(2)
    if not loaded:
        raise RuntimeError("Kulüp bilgileri alınamadı")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, 'html.parser')

    try:
        id_match = re.search(r"/([0-9a-f]{8})(?:/|$)", url)
        club.club_id = id_match.group(1) if id_match else None
    except Exception as e:
        print(f"club_id alınamadı: {e}")
        club.club_id = None

    info = soup.select_one('div[data-template="Partials/Teams/Summary"]')
    if info:
        head = info.select_one("h1")
        if head:
            head_span = head.select_one("span")
            texts = head_span.text.strip().split(" ") if head_span else [t for t in head.text.split() if t]
            try:
                club.season = texts[0]
            except Exception as e:
                print(f"Sezon bilgisi alınamadı {e}")

            try:
                club.club_name = " ".join(texts[1:texts.index("Stats")]) if "Stats" in texts else " ".join(texts[1:])
            except Exception as e:
                print(f"Kulüp ismi alınamadı {e}")

        paragraphs = info.select('p')
        for p in paragraphs:
            try:
                strong = p.select_one("strong")
                if strong and strong.text.strip() == "Governing Country:":
                    club.country_name = p.select_one("a").text.strip()
            except Exception as e:
                print(f"Ülke bilgisi alınamadı {e}")
    return club

async def main():
    browser = await start_browser()
    try:
        url = "https://fbref.com/en/squads/18bb7c10/2025-2026/Arsenal-Stats"
        page = await browser.get(url)

        club = await club_info_scraper(page, url)
        print(club)
    finally:
        browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())