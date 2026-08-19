import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.types import Events, Substitution, CardEvent, GoalInfo, MissPenalty

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

    players = info_div.select("a")
    icon = info_div.select_one("div[class*='event_icon']")
    icon_class = " ".join(icon.get("class", [])) if icon else ""

    if "goal" in icon_class and "own_goal" not in icon_class:
        return GoalInfo(
            scored_by = players[0].text.strip() if players[0].text.strip() else None,
            assist_by= players[1].text.strip() if len(players) > 1 else None,
            minutes = minute,
        )

    elif "own_goal" in icon_class:
        return GoalInfo(
            scored_by = players[0].text.strip() if players[0].text.strip() else None,
            is_own_goal=True,
            minutes = minute,
        )

    elif "penalty_miss" in icon_class:
        return GoalInfo(
            scored_by = players[0].text.strip() if players[0].text.strip() else None,
            minutes = minute,
        )


    elif "yellow_card" in icon_class:
        return CardEvent(
            player_name= players[0].text.strip() if players[0].text.strip() else None,
            minutes = minute,
            card_type= "yellow_card",
        )


    elif "red_card" in icon_class:
        return CardEvent(
            player_name= players[0].text.strip() if players[0].text.strip() else None,
            minutes = minute,
            card_type= "red_card",
            red_type= "direct",
        )

    elif "yellow_red_card" in icon_class:
        return CardEvent(
            player_name= players[0].text.strip() if players[0].text.strip() else None,
            minutes = minute,
            card_type= "red_card",
            red_type= "two_yellow",
        )

    elif "substitute_in" in icon_class:
        return Substitution(
            player_enter= players[0].text.strip() if players[0].text.strip() else None,
            player_exit= players[1].text.strip() if len(players) > 1 else None,
            minutes = minute,
        )

    return None

async def scrapper(page, url):

    try:
        print("Scrapping events")
        await page.select('div[id="events_wrap"]')
    except Exception:
        raise RuntimeError(f"Olaylar alınamadı {url}")

    events_ = Events()

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
    url = "https://fbref.com/en/matches/675b328b/Argentina-Cabo-Verde-July-3-2026-World-Cup"

    page = await browser.get(url)
    event_results = await scrapper(page, url)
    print(event_results)
    browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
