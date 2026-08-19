import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.types import events, substitution, card_event, goal_info

def event_scrapper(content):
    classes = content.get('class', None)

    info_div = content.select('div')[1]
    if not info_div:
        print("Event bilgisi alınamadı")
        return None

    try:
        minute_div = info_div.select('div')[0]
        minute = "".join(minute_div.find_all(string=True, recursive=False)).strip()
        minute = minute.replace("&nbsp9;", "").strip()
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



async def scrapper(page, url):

    event = events()

    try:
        print("Scrapping events")
        await page.wait_for('div[id="events_wrap"]')
    except Exception:
        raise RuntimeError(f"Olaylar alınamadı {url}")

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
            event.home_events = home_events

    if not away_events_list:
        print("Deplasman eventleri alınamadı")
    else:
        away_events = []
        for event in away_events_list:
            event_obj = event_scrapper(event)
            if event_obj:
                away_events.append(event_obj)

        if away_events:
            event.away_events = away_events

    print(away_events, home_events)



async def main():
    browser = await uc.start(headless=False, no_sandbox=True )
    url = "https://fbref.com/en/matches/91a56b43/Genclerbirligi-Fenerbahce-August-15-2026-Super-Lig"

    page = await browser.get(url)
    await scrapper(page, url)
    browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
