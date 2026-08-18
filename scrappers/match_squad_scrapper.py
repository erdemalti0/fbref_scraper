import sys
from bs4 import BeautifulSoup
from pathlib import Path
import nodriver as uc

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.types import match_squad, player_info

def squad_scrapper(content):
    first_eleven = []

    i = 0
    while i < len(content):
        if content[i].select("th"):
            i += 1
            break

        try:
            player_name = content[i].select_one("a").text.strip()
            player_number = content[i].select("td")[0].text.strip()
            player_obj = player_info(
                player_name=player_name,
                player_number=player_number,
            )

            first_eleven.append(player_obj)
        except Exception:
            print("Oyuncu verisi çekme başarısız")

        i += 1

    bench = []
    while i < len(content):
        try:
            player_name = content[i].select_one("a").text.strip()
            player_number = content[i].select("td")[0].text.strip()
            player_obj = player_info(
                player_name=player_name,
                player_number=player_number,
            )

            bench.append(player_obj)
        except Exception:
            print("Oyuncu verisi çekme başarısız")

        i += 1

    return first_eleven, bench


async def scrapper(page, url: str) -> match_squad:

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

            home_first_eleven, home_bench = squad_scrapper(home_table[1::])

        if away_squad_table:
            away_table = away_squad_table[0].select("tr")
            away_lineup = away_table[0].select_one("th").text.split(" ")[-1].lstrip("(").rsplit(")")[0]

            away_first_eleven, away_bench = squad_scrapper(away_table[1::])

    squad_obj = match_squad(
        home_lineup=home_lineup,
        away_lineup=away_lineup,
        home_first_eleven=home_first_eleven,
        home_bench=home_bench,
        away_first_eleven=away_first_eleven,
        away_bench=away_bench,
    )

    return squad_obj

async def main():
    browser = await uc.start(headless=False)
    url = "https://fbref.com/en/matches/91a56b43/Genclerbirligi-Fenerbahce-August-15-2026-Super-Lig"

    page = await browser.get(url)
    squad = await scrapper(page, url)
    print(squad)
    browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
