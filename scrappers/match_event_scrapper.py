import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.types import events, substitution, card_event, goal_info, miss_penalty

def event_scrapper(content):
    classes = content.get('class', None)

    info_div = content.select('div')[1]
    if not info_div:
        print("Event bilgisi alınamadı")
        return None

    try:
        minute_div = content.select('div')[0]
        minute = "".join(minute_div.find_all(string=True, recursive=False)).strip()
        minute = minute.replace("&nbsp9;", "").strip().replace("'", "")
    except Exception as e:
        minute = None
        print(f"Dakika bilgisi alınamadı {e}")

    if info_div.select_one('div[class="event_icon goal"]'):
        event_obj = goal_info()
        event_obj.minutes = minute

        try:
            scored_by = info_div.select("a")[0].text.strip()
            event_obj.scored_by = scored_by
        except Exception as e:
            event_obj.scored_by = None
            print(f"Gol atan oyuncu bulunamadı. {e}")

        if len(info_div.select("a")) > 1:
            try:
                asist_by = info_div.select("a")[1].text.strip()
                event_obj.asist_by = asist_by
            except Exception as e:
                event_obj.asist_by = None
                print(f"Asist yapan oyuncu bulunamadı")
        else:
            event_obj.asist_by = None

        return event_obj

    elif info_div.select_one('div[class="event_icon own_goal"]'):
        event_obj = goal_info()
        event_obj.minutes = minute
        event_obj.isOwnGoal = True

        try:
            player_name = info_div.select_one("a").text.strip()
            event_obj.player_name = player_name
        except Exception as e:
            print(f"Oyuncu ismi alınamadı {e}")

        return event_obj
    elif info_div.select_one('div[class="event_icon penalty_miss"]'):
        event_obj = miss_penalty()
        event_obj.minutes = minute

        try:
            player_name = info_div.select_one("a").text.strip()
            event_obj.player_name = player_name
        except Exception as e:
            print(f"Oyuncu ismi alınamadı {e}")

        return event_obj

    elif info_div.select_one('div[class="event_icon yellow_card"]'):
        event_obj = card_event()
        event_obj.minutes = minute
        event_obj.card_type = "yellow_card"

        try:
            player_name = info_div.select_one("a").text.strip()
            event_obj.player_name = player_name
        except Exception as e:
            event_obj.player_name = None
            print(f"Oyuncu ismi alınamadı {e}")

        return event_obj

    elif info_div.select_one('div[class="event_icon red_card"]'):
        event_obj = card_event()
        event_obj.minutes = minute

        event_obj.card_type = "red_card"
        event_obj.red_type = ("direct")
        try:
            player_name = info_div.select_one("a").text.strip()
            event_obj.player_name = player_name
        except Exception as e:
            event_obj.player_name = None
            print(f"Oyuncu ismi alınamadı {e}")

        return event_obj

    elif info_div.select_one('div[class="event_icon yellow_red_card"]'):
        event_obj = card_event()
        event_obj.minutes = minute

        event_obj.card_type = "red_card"
        event_obj.red_type = ("two_yellow")
        try:
            player_name = info_div.select_one("a").text.strip()
            event_obj.player_name = player_name
        except Exception as e:
            event_obj.player_name = None
            print(f"Oyuncu ismi alınamadı {e}")

        return event_obj

    elif info_div.select_one('div[class="event_icon substitute_in"]'):
        event_obj = substitution()
        event_obj.minutes = minute

        try:
            player_enter = info_div.select("a")[0].text.strip()
            event_obj.player_enter = player_enter
        except Exception as e:
            event_obj.player_enter = None
            print(f"Giren oyuncu ismi alınamadı {e}")

        try:
            player_exit = info_div.select("a")[1].text.strip()
            event_obj.player_exit = player_exit
        except Exception as e:
            event_obj.player_exit = None
            print(f"Çıkan oyuncu ismi alınamadı {e}")

        return event_obj

    return None

async def scrapper(page, url):

    try:
        print("Scrapping events")
        await page.select('div[id="events_wrap"]')
    except Exception:
        raise RuntimeError(f"Olaylar alınamadı {url}")

    events_ = events()

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    event_section = soup.select_one('div[id="events_wrap"]')

    if not event_section:
        raise RuntimeError(f"Event alanı bulunamadı {url}")

    home_events_list = event_section.select('div[class="event a"]')
    away_events_list = event_section.select('div[class="event b"]')

    if not home_events_list:
        print("Ev sahibi eventleri alınamadı.")
    else:
        home_events = []
        for event in home_events_list:
            event_obj = event_scrapper(event)
            if event_obj:
                home_events.append(event_obj)

        if home_events:
            events_.home_events = home_events

    if not away_events_list:
        print("Deplasman eventleri alınamadı")
    else:
        away_events = []
        for event in away_events_list:
            event_obj = event_scrapper(event)
            if event_obj:
                away_events.append(event_obj)

        if away_events:
            events_.away_events = away_events

    return events_


async def main():
    browser = await uc.start(headless=False, no_sandbox=True )
    url = "https://fbref.com/en/matches/dc6c3a39/Galatasaray-Yeni-Corumspor-August-14-2026-Super-Lig"

    page = await browser.get(url)
    event_results = await scrapper(page, url)
    browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
