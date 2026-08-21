import sys
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import nodriver as uc

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.match_report_types import GeneralMatchInfo, GoalInfo, normalize_minute
from core.browser import start_browser

def goal_list_creator(content) -> list:
    goals_list = []
    for goal in content:
        icon = goal.select_one("div[class*='event_icon']")
        icon_class = " ".join(icon.get("class", [])) if icon else ""

        # goal, own_goal ve penalty_goal ikonlarının hepsi gol sayılır
        if "goal" not in icon_class:
            continue

        scorer_tag = goal.select_one("a[href*='player']")
        scorer = scorer_tag.text.strip() if scorer_tag else None
        text = goal.text.strip()

        is_penalty = "(P)" in text
        is_own_goal = "(OG)" in text or "own_goal" in icon_class
        minute = normalize_minute(text.split(" ")[-1])

        goal_obj = GoalInfo(
            scorer=scorer,
            minute=minute,
            is_penalty=is_penalty,
            is_own_goal=is_own_goal,
        )

        goals_list.append(goal_obj)

    return goals_list

async def match_general_info_scraper(page ,url: str) -> GeneralMatchInfo:

    info_obj = GeneralMatchInfo()

    try:
        print("Scrapping: " + url)
        await page.wait_for('div.scorebox')
    except Exception:
        raise RuntimeError(f"Sayfa alınamadı {url}")

    print("Scrapping başarılı")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, 'html.parser')

    scorebox = soup.find('div', class_='scorebox')
    if not scorebox:
        raise RuntimeError(f"Scorebox bulunamadı: {url}")

    # Match id from url
    try:
        info_obj.match_id = url.split("/")[5]
    except Exception as e:
        print(f"match_id alınamadı: {e}")
        info_obj.match_id = None

    scorebox_meta = soup.select_one('div[class="scorebox_meta"]')

    # Match date
    try:
        data = " ".join(scorebox_meta.select_one('a[href*="/matches/"]').text.strip().replace(",", "").split(" ")[1::])
        info_obj.match_date = datetime.strptime(data, "%B %d %Y")
    except Exception as e:
        print(f"match_date alınamadı: {e}")
        info_obj.match_date = None

    # League
    try:
        info_obj.league = scorebox_meta.select_one('a[href*="/comps/"]').text.strip()
    except Exception as e:
        print(f"league alınamadı: {e}")
        info_obj.league = None

    try:
        smalls = scorebox_meta.select("small")
        for i, small in enumerate(smalls):
            label = small.text.strip()
            try:
                if label == "Attendance":
                    info_obj.attendance = int(smalls[i+1].text.strip().replace(",", ""))
                elif label == "Venue":
                    info_obj.venue = smalls[i+1].text.strip()
                elif label == "Officials":
                    spans = smalls[i+1].select("span")
                    if spans:
                        info_obj.referee = spans[0].text.strip().replace("\xa0", " ").replace("(Referee)", "").strip()
            except Exception as e:
                print(f"{label} alınamadı: {e}")
    except Exception as e:
        print(f"Scorebox meta bilgileri alınamadı: {e}")

    home_team_html = scorebox.find('div', id='sb_team_0')
    away_team_html = scorebox.find('div', id='sb_team_1')

    # Home team name
    try:
        info_obj.home_name = home_team_html.select_one("a[href*='/squads/']").text.strip()
    except Exception as e:
        print(f"home_name alınamadı: {e}")
        info_obj.home_name = None

    # Home manager
    # Datapoint is a class in this html code there is a 2 datapoint one of it
    # give us a manager information other one captain
    try:
        datapoints = home_team_html.select('div[class="datapoint"]')
        info_obj.home_manager = datapoints[0].text.strip().replace("Manager: ", "").replace("\xa0", " ")
    except Exception as e:
        print(f"home_manager alınamadı: {e}")
        info_obj.home_manager = None

    # Home captain
    try:
        datapoints = home_team_html.select('div[class="datapoint"]')
        info_obj.home_captain = datapoints[1].select_one("a").text.strip().replace("\xa0", " ")
    except Exception as e:
        print(f"home_captain alınamadı: {e}")
        info_obj.home_captain = None

    # Away team name
    try:
        info_obj.away_name = away_team_html.select_one("a[href*='/squads/']").text.strip()
    except Exception as e:
        print(f"away_name alınamadı: {e}")
        info_obj.away_name = None

    # Away manager
    try:
        datapoints = away_team_html.select('div[class="datapoint"]')
        info_obj.away_manager = datapoints[0].text.strip().replace("Manager: ", "").replace("\xa0", " ")
    except Exception as e:
        print(f"away_manager alınamadı: {e}")
        info_obj.away_manager = None

    # Away captain
    try:
        datapoints = away_team_html.select('div[class="datapoint"]')
        info_obj.away_captain = datapoints[1].select_one("a").text.strip().replace("\xa0", " ")
    except Exception as e:
        print(f"away_captain alınamadı: {e}")
        info_obj.away_captain = None

    # Scores
    try:
        scores = soup.find_all("div", class_="score")
        info_obj.home_goals = int(scores[0].text.strip())
        info_obj.away_goals = int(scores[1].text.strip())
    except Exception as e:
        print(f"skorlar alınamadı: {e}")
        info_obj.home_goals = None
        info_obj.away_goals = None

    # Home goal scorers
    try:
        goals_html = scorebox.select("div[class='event']")
        home_goals_html = goals_html[0].select("div")
        info_obj.home_goal_scorers = goal_list_creator(home_goals_html)
    except Exception as e:
        print(f"home_goal_scorers alınamadı: {e}")
        info_obj.home_goal_scorers = None

    # Away goal scorers
    try:
        goals_html = scorebox.select("div[class='event']")
        away_goals_html = goals_html[1].select("div")
        info_obj.away_goal_scorers = goal_list_creator(away_goals_html)
    except Exception as e:
        print(f"away_goal_scorers alınamadı: {e}")
        info_obj.away_goal_scorers = None

    return info_obj

async def main():

    browser = await start_browser(headless=False)
    try:
        url = "https://fbref.com/en/matches/675b328b/Argentina-Cabo-Verde-July-3-2026-World-Cup"
        page = await browser.get(url)
        result = await match_general_info_scraper(page, url)
        print(result)
    finally:
        browser.stop()
if __name__ == "__main__":

    uc.loop().run_until_complete(main())
