import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.types import events, substitution, card_event, goal_info

def event_scrapper(content):
    if content.select_one('class[id="event_icon goal"]'):
        event_obj = goal_info()
        info = content.select('a[href*="/player/"')
        if info:
            goal_scorer = info[0].text.strip()
            event_obj["goal_scorer"] = goal_scorer if goal_scorer else None

            asist_maker = info[1].text.strip()
            event_obj["asist_maker"] = asist_maker if asist_maker else None

            min_html = content.select_one('div')
            if min_html:
                mininute = "".join([c for c in min_html.text if c.isdigit()])
                event_obj["minutes"] = mininute if mininute else None
            else:
                event_obj["minutes"] = None

    elif content.select_one('class[id="event_icon yellow_card"]'):
        info = content.select_one('a[href*="/player/"')
        if info:
            player_name = info[0].text.strip()
        else:
            player_name = None




async def scrapper(page, url):

    try:
        print("Scrapping events")
        await page.wait_for('div[id="events_wrap"]')
    except Exception:
        raise RuntimeError(f"Olaylar alınamadı {url}")

    home_event = {

    }
    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, 'html.parser')

    events_html = soup.select_one('div[id="events_wrap"]')

    try:
        if events_html:
            home_events = events_html.select('div[id="event a"]')
            away_events = events_html.select('div[id="event b"]')

            if home_events:


    except:
        pass

async def main():

    browser = uc.start(headless=False)
    url = "https://fbref.com/en/matches/91a56b43/Genclerbirligi-Fenerbahce-August-15-2026-Super-Lig"

    page = await browser.get(url)
    await scrapper(page, url)
    browser.close()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
