import sys
from bs4 import BeautifulSoup
from pathlib import Path
import nodriver as uc

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.types import match_squad, general_match_info


def squad_scrapper(content) -> dict:


async def scrapper(page, url: str) -> general_match_info:

    try:
        print("Scrapping Squad")
        await page.wait_for('div[class="field_wrap"]')
    except Exception:
        RuntimeError(f"Kadrolar alınamadı {url}")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    squad_field = soup.select('div[class="lineup"]')

    if squad_field:
        home_squad_table = squad_field[0].select("tbody")
        away_squad_table = squad_field[1].select("tbody")

        if home_squad_table:
            home_table = home_squad_table[0].select("tr")
            home_lineup = home_table[0].select_one("th").text.split(" ")[-1].lstrip("(").rsplit(")")[0]








async def main():
    browser = await uc.start(headless=False)
    url = "https://fbref.com/en/matches/91a56b43/Genclerbirligi-Fenerbahce-August-15-2026-Super-Lig"

    page = await browser.get(url)
    await scrapper(page, url)
    browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
