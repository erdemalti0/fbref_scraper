import sys
from bs4 import BeautifulSoup
from pathlib import Path
import nodriver as uc

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.match_report_types import MatchSquad, PlayerInfo
from core.browser import start_browser

def parse_squad(table_rows):
    starting_eleven = []

    i = 0
    while i < len(table_rows):
        if table_rows[i].select("th"):
            i += 1
            break

        try:
            player_name = table_rows[i].select_one("a").text.strip()
            player_number = table_rows[i].select("td")[0].text.strip()
            player_obj = PlayerInfo(
                name=player_name,
                number=int(player_number) if player_number.isdigit() else None,
            )

            starting_eleven.append(player_obj)
        except Exception as e:
            print(f"Oyuncu verisi çekme başarısız: {e}")

        i += 1

    bench = []
    while i < len(table_rows):
        try:
            player_name = table_rows[i].select_one("a").text.strip()
            player_number = table_rows[i].select("td")[0].text.strip()
            player_obj = PlayerInfo(
                name=player_name,
                number=int(player_number) if player_number.isdigit() else None,
            )

            bench.append(player_obj)
        except Exception as e:
            print(f"Oyuncu verisi çekme başarısız: {e}")

        i += 1

    return starting_eleven, bench


async def match_squad_scraper(page) -> MatchSquad:

    squad_obj = MatchSquad()

    try:
        print("Scrapping Squad")
        await page.wait_for('div[class="lineup"]')
    except Exception:
        raise RuntimeError("Kadrolar alınamadı")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    lineup_divs = soup.select('div[class="lineup"]')
    if not lineup_divs:
        raise RuntimeError("Kadro alanı bulunamadı")

    # Home squad
    try:
        home_squad_table = lineup_divs[0].select("tbody")
        home_table = home_squad_table[0].select("tr")
    except Exception as e:
        print(f"home kadro tablosu alınamadı: {e}")
        home_table = []

    # Home formation
    try:
        squad_obj.home_formation = home_table[0].select_one("th").text.split(" ")[-1].lstrip("(").rsplit(")")[0]
    except Exception as e:
        print(f"home_formation alınamadı: {e}")
        squad_obj.home_formation = None

    # Home starting eleven and bench
    try:
        home_starting_eleven, home_bench = parse_squad(home_table[1::])
        squad_obj.home_starting_eleven = home_starting_eleven
        squad_obj.home_bench = home_bench
    except Exception as e:
        print(f"home ilk 11 / yedekler alınamadı: {e}")
        squad_obj.home_starting_eleven = None
        squad_obj.home_bench = None

    # Away squad
    try:
        away_squad_table = lineup_divs[1].select("tbody")
        away_table = away_squad_table[0].select("tr")
    except Exception as e:
        print(f"away kadro tablosu alınamadı: {e}")
        away_table = []

    # Away formation
    try:
        squad_obj.away_formation = away_table[0].select_one("th").text.split(" ")[-1].lstrip("(").rsplit(")")[0]
    except Exception as e:
        print(f"away_formation alınamadı: {e}")
        squad_obj.away_formation = None

    # Away starting eleven and bench
    try:
        away_starting_eleven, away_bench = parse_squad(away_table[1::])
        squad_obj.away_starting_eleven = away_starting_eleven
        squad_obj.away_bench = away_bench
    except Exception as e:
        print(f"away ilk 11 / yedekler alınamadı: {e}")
        squad_obj.away_starting_eleven = None
        squad_obj.away_bench = None

    return squad_obj

async def main():
    browser = await start_browser(headless=False)
    try:
        url = "https://fbref.com/en/matches/91a56b43/Genclerbirligi-Fenerbahce-August-15-2026-Super-Lig"

        page = await browser.get(url)
        squad = await match_squad_scraper(page)
        #print(squad)
    finally:
        browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
