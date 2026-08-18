import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.types import match_squad, player_info

async def scrapper(page, url):

    try:
        print("Scrapping events")
        await page.wait_for('div[id="events_wrap"]')
    except Exception:
        RuntimeError(f"Olaylar alınamadı {url}")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, 'html.parser')

    events_html = soup.select_one('div[id="events_wrap"]')

    try:
        if events_html:
            home_events = events_html.select('div[id="event a"]')
            away_events = events_html.select('div[id="event b"]')

            if home_events:


    except:
        pass

async def main():

    browser = uc.start(headless=False)
    url = "https://fbref.com/en/matches/91a56b43/Genclerbirligi-Fenerbahce-August-15-2026-Super-Lig"

    page = await browser.get(url)
    await scrapper(page, url)
    browser.close()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
