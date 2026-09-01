import sys
from bs4 import BeautifulSoup
from pathlib import Path
import nodriver as uc

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.match_report_types import MatchSquad, PlayerInfo
from core.browser import start_browser
from core.logger import get_logger

logger = get_logger(__name__)

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
            logger.warning(f"Starting eleven player could not be parsed: {e}")

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
            logger.warning(f"Bench player could not be parsed: {e}")

        i += 1

    return starting_eleven, bench


def parse_lineup(lineup_div) -> tuple[str, list[PlayerInfo], list[PlayerInfo]]:
    table = lineup_div.select("tbody")[0].select("tr")
    formation = table[0].select_one("th").text.split(" ")[-1].lstrip("(").rsplit(")")[0]
    starting_eleven, bench = parse_squad(table[1::])
    return formation, starting_eleven, bench


async def match_squad_scraper(page) -> MatchSquad:

    squad_obj = MatchSquad()

    try:
        logger.info("Scraping squad")
        await page.wait_for('div[class="lineup"]')
    except Exception:
        raise RuntimeError("Squad section could not be loaded")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    lineup_divs = soup.select('div[class="lineup"]')
    if not lineup_divs:
        raise RuntimeError("Squad section not found in page")

    # Home squad
    try:
        squad_obj.home_formation, squad_obj.home_starting_eleven, squad_obj.home_bench = parse_lineup(lineup_divs[0])
    except Exception as e:
        logger.warning(f"Home squad could not be parsed: {e}")

    # Away squad
    try:
        squad_obj.away_formation, squad_obj.away_starting_eleven, squad_obj.away_bench = parse_lineup(lineup_divs[1])
    except Exception as e:
        logger.warning(f"Away squad could not be parsed: {e}")

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
