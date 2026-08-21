import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.player_page_types import PlayerInfo
from core.browser import start_browser

async def player_info_scraper(page, url) -> PlayerInfo | None:
    player_obj = PlayerInfo()

    try:
        player_obj.player_id = url.split("/")[5]
    except Exception as e:
        print(f"Oyuncu id si alınamadı: {e}")

    try:
        print("Oyuncu bilgileri alınıyor")
        await page.select('div[id="meta"]')
    except Exception as e:
        print(f"Oyuncu bilgileri alınamadı {e}")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    meta_html = soup.select_one('div[id="meta"]')
    if meta_html:
        try:
            player_obj.player_name = meta_html.select_one('h1').text.strip()
        except Exception as e:
            print(f"Oyuncu ismi alınamadı {e}")

        others = meta_html.select('p')
        if others:
            try:
                player_obj.player_full_name = others[0].text.strip()
            except Exception as e:
                print(f"Tam isim alınamadı {e}")

            try:
                player_obj.player_position = others[1].find(string=True, recursive=False).text.strip()
            except Exception as e:
                print(f"Oyuncu pozisyonu alınamadı")

            try:
                player_obj.player_height = int("".join([i for i in others[2].select("span")[0].text.strip() if i.isdigit()]))
            except Exception as e:
                print(f"Oyuncu boyu alınamadı")

            try:
                player_obj.player_weight = int("".join([i for i in others[2].select("span")[1].text.strip() if i.isdigit()]))
            except Exception as e:
                print(f"Oyuncu kilosu alınamadı {e}")

            try:
                data = others[3].select("span")[0].text.strip().replace(",", "")
                player_obj.player_birth_date = datetime.strptime(data, "%B %d %Y")
            except Exception as e:
                print(f"Oyuncu doğum günü alınamadı {e}")

            try:
                born_place_parts = others[3].select("span")[1].text.strip().split(" ")
                player_obj.player_born_place = " ".join(born_place_parts[1::]).strip()
            except Exception as e:
                print(f"Oyuncu doğum yeri alınamadı {e}")

            try:
                data = others[4].select("a")
                if len(data) > 1:
                    player_obj.player_national_team = data[0].text.strip()
                    player_obj.player_other_national_team = data[1].text.strip()
                else:
                    player_obj.player_national_team = data[0].text.strip()
            except Exception as e:
                print(f"Oyuncu milli takım bilgisi alınamadı")

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