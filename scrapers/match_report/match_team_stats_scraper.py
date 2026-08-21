import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.match_report_types import TeamStats
from core.browser import start_browser
async def team_stats_scraper(page):

    try:
        print("Scrapping team stats")
        await page.select('div[id="team_stats"]')
        await page.select('div[id="team_stats_extra"]')
    except Exception as e:
        print(f"Takım statları alınamadı {e}")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, 'html.parser')
    stats = TeamStats()
    team_stats = soup.find('table', style='table-layout: fixed;')

    if team_stats:
        team_names = team_stats.select('span[class="teamandlogo"]')
        rows = team_stats.select('tr')

        if team_names:
            try:
                stats.home_name = team_names[0].text.strip() if team_names[0] else None
                stats.away_name = team_names[1].text.strip() if team_names[1] else None
            except Exception as e:
                print(f"Takım adları alınamadı {e}")
        else:
            print("Takım adları bulunamadı")

        if len(rows) > 2:
            possesion_infos = rows[2].select("strong")
            try:
                home_possession = int(possesion_infos[0].text.strip().replace("%", ""))
                away_possession = int(possesion_infos[1].text.strip().replace("%", ""))
                if home_possession + away_possession == 101:
                    home_possession = home_possession - 0.5
                    away_possession = away_possession - 0.5
                stats.home_possession = float(home_possession)
                stats.away_possession = float(away_possession)
            except Exception as e:
                print(f"Topla oynama bilgileri alınamadı {e}")
        else:
            print("Topla oynama bilgileri bulunamadı")

        if len(rows) > 4:
            shot_infos = rows[4].select("td")
            if shot_infos:
                parsed_home_shots = shot_infos[0].text.replace("\xa0", "").replace("\n", "").replace("—", " ").split(" ")
                parsed_away_shots = shot_infos[1].text.replace("\xa0", "").replace("\n", "").replace("—", " ").split(" ")
                if parsed_home_shots:

                    try:
                        stats.home_shots = int(parsed_home_shots[2]) if parsed_home_shots[1] else None
                        stats.home_shots_on_target = int(parsed_home_shots[0]) if parsed_home_shots[0] else None
                        stats.home_missed_shots = stats.home_shots - stats.home_shots_on_target if stats.home_shots_on_target else stats.home_shots
                    except Exception as e:
                        print(f"Ev sahibi şut bilgileri alınamadı {e}")

                if parsed_away_shots:
                    try:
                        stats.away_shots = int(parsed_away_shots[3]) if parsed_away_shots[1] else None
                        stats.away_shots_on_target = int(parsed_away_shots[1]) if parsed_away_shots[0] else None
                        stats.away_missed_shots = stats.away_shots - stats.away_shots_on_target if stats.away_shots_on_target else stats.away_shots
                    except Exception as e:
                        print(f"Deplasman şut bilgileri alınamadı {e}")

            if len(rows) > 6:
                save_info = rows[6].select("td")
                if save_info:
                    parsed_home_saves = save_info[0].text.replace("\xa0", "").replace("\n", "").replace("—", " ").split(" ")
                    parsed_away_saves = save_info[1].text.replace("\xa0", "").replace("\n", "").replace("—", " ").split(" ")
                    if parsed_home_saves:

                        try:
                            stats.home_saves = int(parsed_home_saves[0]) if parsed_home_saves[0] else None
                        except Exception as e:
                            print(f"Ev sahibi kurtarış bilgileri alınamadı {e}")

                    if parsed_away_saves:
                        try:
                            stats.away_saves = int(parsed_away_saves[1]) if parsed_away_saves[1] else None
                        except Exception as e:
                            print(f"Deplasman kurtarış bilgileri alınamadı {e}")

            if len(rows) > 8:
                card_infos = rows[8].select("td")
                if card_infos:
                    try:
                        stats.home_yellow_cards = len(card_infos[0].select('span[class="yellow_card"]'))
                        stats.home_red_cards = len(card_infos[0].select('span[class="red_card"]'))

                        stats.away_yellow_cards = len(card_infos[1].select('span[class="yellow_card"]'))
                        stats.away_red_cards = len(card_infos[1].select('span[class="red_card"]'))

                    except Exception as e:
                        print(f"Kart bilgileri çekilemedi {e}")

                    if card_infos[0].select('span[class="yellow_red_card"]'):

                        try:
                            stats.home_red_cards = (stats.home_red_cards or 0) + len(card_infos[0].select('span[class="yellow_red_card"]'))
                        except Exception as e:
                            pass

                    elif card_infos[1].select('span[class="yellow_red_card"]'):
                        try:
                            stats.away_red_cards = (stats.away_red_cards or 0) + len(card_infos[1].select('span[class="yellow_red_card"]'))
                        except Exception as e:
                            pass

        extra = soup.find('div', id='team_stats_extra')
        if extra:
            divs = extra.select('div')
            try:
                for div in divs:
                    divs2 = div.select('div')
                    for i, d in enumerate(divs2):
                        if i == 0 or i + 1 >= len(divs2):
                            continue
                        if d.text == "Fouls":
                            stats.home_fouls = int(divs2[i - 1].text)
                            stats.away_fouls = int(divs2[i + 1].text)
                        elif d.text == "Corners":
                            stats.home_corners = int(divs2[i - 1].text)
                            stats.away_corners = int(divs2[i + 1].text)
                        elif d.text == "Crosses":
                            stats.home_crosses = int(divs2[i - 1].text)
                            stats.away_crosses = int(divs2[i + 1].text)
                        elif d.text == "Interceptions":
                            stats.home_interceptions = int(divs2[i - 1].text)
                            stats.away_interceptions = int(divs2[i + 1].text)
                        elif d.text == "Offsides":
                            stats.home_offsides = int(divs2[i - 1].text)
                            stats.away_offsides = int(divs2[i + 1].text)
            except Exception as e:
                print(f"Extra stat bilgileri alınamadı {e}")

    else:
        print("Team stats çekilemedi")

    return stats

async def main():
    browser = await start_browser(headless=False)
    try:
        url = "https://fbref.com/en/matches/9fd14983/Netherlands-Argentina-December-9-2022-World-Cup"
        page = await browser.get(url)

        result = await team_stats_scraper(page)
        print(result)
    finally:
        browser.stop()
if __name__ == "__main__":
    uc.loop().run_until_complete(main())