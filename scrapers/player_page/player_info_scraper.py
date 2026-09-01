import sys
import re
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.player_page_types import PlayerInfo
from core.browser import start_browser
from core.logger import get_logger

logger = get_logger(__name__)

KNOWN_LABELS = ("Position:", "Born:", "National Team:", "Club:", "Wages:", "Also Played As:", "Instagram:", "Twitter:", "Facebook:")

async def player_info_scraper(page, url) -> PlayerInfo | None:
    player_obj = PlayerInfo()

    try:
        id_match = re.search(r"/([0-9a-f]{8})(?:/|$)", url)
        player_obj.player_id = id_match.group(1) if id_match else None
    except Exception as e:
        logger.warning(f"player_id could not be parsed: {e}")

    try:
        logger.info("Scraping player info")
        await page.select('div[id="meta"]')
    except Exception as e:
        logger.warning(f"Player meta section could not be loaded: {e}")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    meta_html = soup.select_one('div[id="meta"]')
    if meta_html:
        try:
            player_obj.player_name = meta_html.select_one('h1').text.strip()
        except Exception as e:
            logger.warning(f"Player name could not be parsed: {e}")

        others = [p for p in meta_html.select('p') if p.text.strip()]

        full_name_ps = [p for p in others if not p.text.strip().startswith(KNOWN_LABELS) and "cm" not in p.text]
        if full_name_ps:
            try:
                player_obj.player_full_name = full_name_ps[0].text.strip()
            except Exception as e:
                logger.warning(f"Player full name could not be parsed: {e}")

        position_p = next((p for p in others if "Position:" in p.text), None)
        if position_p:
            try:
                position_text = position_p.text.strip().replace("Position:", "").split("▪")[0]
                player_obj.player_position = position_text.replace("\xa0", " ").strip()
            except Exception as e:
                logger.warning(f"Player position could not be parsed: {e}")

        physical_p = next((p for p in others if "cm" in p.text), None)
        if physical_p:
            try:
                player_obj.player_height = int("".join([i for i in physical_p.select("span")[0].text.strip() if i.isdigit()]))
            except Exception as e:
                logger.warning(f"Player height could not be parsed: {e}")

            try:
                player_obj.player_weight = int("".join([i for i in physical_p.select("span")[1].text.strip() if i.isdigit()]))
            except Exception as e:
                logger.warning(f"Player weight could not be parsed: {e}")

        born_p = next((p for p in others if "Born:" in p.text), None)
        if born_p:
            try:
                data = born_p.select("span")[0].text.strip().replace(",", "")
                player_obj.player_birth_date = datetime.strptime(data, "%B %d %Y")
            except Exception as e:
                logger.warning(f"Player birth date could not be parsed: {e}")

            try:
                place_match = re.search(r"\bin\s+([^\n]+)", born_p.text)
                player_obj.player_born_place = place_match.group(1).strip() if place_match else None
            except Exception as e:
                logger.warning(f"Player birth place could not be parsed: {e}")

        national_p = next((p for p in others if "National Team:" in p.text), None)
        if national_p:
            try:
                data = national_p.select("a")
                if len(data) > 1:
                    player_obj.player_national_team = data[0].text.strip()
                    player_obj.player_other_national_team = data[1].text.strip()
                else:
                    player_obj.player_national_team = data[0].text.strip()
            except Exception as e:
                logger.warning(f"Player national team could not be parsed: {e}")

    return player_obj

async def main():
    browser = await start_browser(headless=False)
    try:
        url = "https://fbref.com/en/players/e6af3cc7/Clarence-Seedorf"

        page = await browser.get(url)
        player_info = await player_info_scraper(page, url)
        print(player_info)
    finally:
        browser.stop()

if "__main__" == __name__:

    uc.loop().run_until_complete(main())
