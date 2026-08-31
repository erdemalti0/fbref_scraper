import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.match_report_types import Events, Substitution, CardEvent, GoalInfo, MissedPenalty, normalize_minute
from core.browser import start_browser

def parse_event(event_div):
    info_div = event_div.select('div')[1]
    if not info_div:
        print("Event bilgisi alınamadı")
        return None

    try:
        minute_div = event_div.select('div')[0]
        minute = "".join(minute_div.find_all(string=True, recursive=False)).strip()
        minute = normalize_minute(minute.replace("\xa0", ""))
    except Exception as e:
        minute = None
        print(f"Dakika bilgisi alınamadı {e}")

    players = info_div.select("a")
    icon = info_div.select_one("div[class*='event_icon']")
    icon_class = " ".join(icon.get("class", [])) if icon else ""

    if "goal" in icon_class and "own_goal" not in icon_class:
        return GoalInfo(
            scorer=players[0].text.strip() if players and players[0].text.strip() else None,
            assist_provider=players[1].text.strip() if len(players) > 1 else None,
            minute=minute,
        )

    elif "own_goal" in icon_class:
        return GoalInfo(
            scorer=players[0].text.strip() if players and players[0].text.strip() else None,
            is_own_goal=True,
            minute=minute,
        )

    elif "penalty_miss" in icon_class:
        return MissedPenalty(
            player_name=players[0].text.strip() if players and players[0].text.strip() else None,
            minute=minute,
        )


    elif "yellow_card" in icon_class:
        return CardEvent(
            player_name=players[0].text.strip() if players and players[0].text.strip() else None,
            minute=minute,
            card_type="yellow_card",
        )


    elif "yellow_red_card" in icon_class:
        return CardEvent(
            player_name=players[0].text.strip() if players and players[0].text.strip() else None,
            minute=minute,
            card_type="red_card",
            red_type="two_yellow",
        )

    elif "red_card" in icon_class:
        return CardEvent(
            player_name=players[0].text.strip() if players and players[0].text.strip() else None,
            minute=minute,
            card_type="red_card",
            red_type="direct",
        )

    elif "substitute_in" in icon_class:
        return Substitution(
            player_in=players[0].text.strip() if players and players[0].text.strip() else None,
            player_out=players[1].text.strip() if len(players) > 1 else None,
            minute=minute,
        )

    return None

async def match_events_scraper(page):

    try:
        print("Scrapping events")
        await page.select('div[id="events_wrap"]')
    except Exception:
        raise RuntimeError("Olaylar alınamadı")

    events = Events()

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    event_section = soup.select_one('div[id="events_wrap"]')

    if not event_section:
        raise RuntimeError("Event alanı bulunamadı")

    home_events_list = event_section.select('div[class="event a"]')
    away_events_list = event_section.select('div[class="event b"]')

    if not home_events_list:
        print("Ev sahibi eventleri alınamadı.")
    else:
        home_events = []
        for event in home_events_list:
            try:
                event_obj = parse_event(event)
            except Exception as e:
                print(f"Event alınamadı {e}")
                continue
            if event_obj:
                home_events.append(event_obj)

        if home_events:
            events.home_events = home_events

    if not away_events_list:
        print("Deplasman eventleri alınamadı")
    else:
        away_events = []
        for event in away_events_list:
            try:
                event_obj = parse_event(event)
            except Exception as e:
                print(f"Event alınamadı {e}")
                continue
            if event_obj:
                away_events.append(event_obj)

        if away_events:
            events.away_events = away_events

    return events


async def main():
    browser = await start_browser(headless=False, no_sandbox=True)
    try:
        url = "https://fbref.com/en/matches/675b328b/Argentina-Cabo-Verde-July-3-2026-World-Cup"

        page = await browser.get(url)
        event_results = await match_events_scraper(page)
        print(event_results)
    finally:
        browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
