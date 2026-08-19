import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

async def scrapper(page):

    try:
        print("Scrapping team stats")
        await page.select('div[id="team_stats"]')
        await page.select('div[id="team_stats_extra"]')
    except Exception as e:
        print(f"Takım statları alınamadı {e}")

    return

async def main():
    browser = uc.start(headless=False)
    url = "https://fbref.com/en/matches/dc6c3a39/Galatasaray-Yeni-Corumspor-August-14-2026-Super-Lig"
    page = await browser.get(url)

    result = await scrapper(page)
    browser.close()
if __name__ == "__main__":
    uc.loop().run_until_complete(main())