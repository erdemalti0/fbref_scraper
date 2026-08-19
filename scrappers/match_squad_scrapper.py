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
        except Exception as e:
            print(f"Oyuncu verisi çekme başarısız: {e}")

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
        except Exception as e:
            print(f"Oyuncu verisi çekme başarısız: {e}")

        i += 1

    return first_eleven, bench


async def scrapper(page, url: str) -> match_squad:

    squad_obj = match_squad()

    try:
        print("Scrapping Squad")
        await page.wait_for('div[class="field_wrap"]')
    except Exception:
        raise RuntimeError(f"Kadrolar alınamadı {url}")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    squad_field = soup.select('div[class="lineup"]')
    if not squad_field:
        raise RuntimeError(f"Kadro alanı bulunamadı: {url}")

    # Home squad
    try:
        home_squad_table = squad_field[0].select("tbody")
        home_table = home_squad_table[0].select("tr")
    except Exception as e:
        print(f"home kadro tablosu alınamadı: {e}")
        home_table = []

    # Home lineup
    try:
        squad_obj.home_lineup = home_table[0].select_one("th").text.split(" ")[-1].lstrip("(").rsplit(")")[0]
    except Exception as e:
        print(f"home_lineup alınamadı: {e}")
        squad_obj.home_lineup = None

    # Home first eleven and bench
    try:
        home_first_eleven, home_bench = squad_scrapper(home_table[1::])
        squad_obj.home_first_eleven = home_first_eleven
        squad_obj.home_bench = home_bench
    except Exception as e:
        print(f"home ilk 11 / yedekler alınamadı: {e}")
        squad_obj.home_first_eleven = None
        squad_obj.home_bench = None

    # Away squad
    try:
        away_squad_table = squad_field[1].select("tbody")
        away_table = away_squad_table[0].select("tr")
    except Exception as e:
        print(f"away kadro tablosu alınamadı: {e}")
        away_table = []

    # Away lineup
    try:
        squad_obj.away_lineup = away_table[0].select_one("th").text.split(" ")[-1].lstrip("(").rsplit(")")[0]
    except Exception as e:
        print(f"away_lineup alınamadı: {e}")
        squad_obj.away_lineup = None

    # Away first eleven and bench
    try:
        away_first_eleven, away_bench = squad_scrapper(away_table[1::])
        squad_obj.away_first_eleven = away_first_eleven
        squad_obj.away_bench = away_bench
    except Exception as e:
        print(f"away ilk 11 / yedekler alınamadı: {e}")
        squad_obj.away_first_eleven = None
        squad_obj.away_bench = None

    return squad_obj

async def main():
    browser = await uc.start(headless=False)
    url = "https://fbref.com/en/matches/91a56b43/Genclerbirligi-Fenerbahce-August-15-2026-Super-Lig"

    page = await browser.get(url)
    squad = await scrapper(page, url)
    #print(squad)
    browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
