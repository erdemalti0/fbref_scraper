import sys
from bs4 import BeautifulSoup
from pathlib import Path
import nodriver as uc

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.types import general_match_info, goal_info

def goal_list_crator(content) -> list:
    goals_list = []
    for goal in content:
        if goal.select_one("div[class='event_icon goal']"):
            scored_by = goal.select_one("a[href*='player']").text.strip()
            if "P" in goal.text.strip():
                isPenalty = True
                isOwnGoal = False
                minutes = goal.text.strip().split(" ")[-1]
            elif "OG" in goal.text.strip():
                isPenalty = False
                isOwnGoal = True
                minutes = goal.text.strip().split(" ")[-1]
            else:
                isPenalty = False
                isOwnGoal = False
                minutes = goal.text.strip().split(" ")[-1]

            goal_obj = goal_info(
                scored_by=scored_by,
                minutes=minutes,
                home_or_away="home",
                isPenalty=isPenalty,
                isOwnGoal=isOwnGoal,
            )

            goals_list.append(goal_obj)

    return goals_list

async def scrapper(page ,url: str) -> general_match_info:

    info_obj = general_match_info()

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

    score_box_meta_html = soup.select_one('div[class="scorebox_meta"]')

    # Match date
    try:
        data = score_box_meta_html.select_one('a[href*="/matches/"]').text.strip().replace(",", "").split(" ")
        info_obj.match_date = f"{data[2]}/{data[1]}/{data[-1]}"
    except Exception as e:
        print(f"match_date alınamadı: {e}")
        info_obj.match_date = None

    # League
    try:
        info_obj.league = score_box_meta_html.select_one('a[href*="/comps/"]').text.strip()
    except Exception as e:
        print(f"league alınamadı: {e}")
        info_obj.league = None

    # Place information in smalls
    try:
        smalls = score_box_meta_html.select("small")
        for i, small in enumerate(smalls):
            if small.text.strip() == "Venue":
                info_obj.match_place = smalls[i+1].text.strip()
                break
    except Exception as e:
        print(f"match_place alınamadı: {e}")
        info_obj.match_place = None

    # Referee information in smalls
    try:
        smalls = score_box_meta_html.select("small")
        for i, small in enumerate(smalls):
            if small.text.strip() == "Officials":
                spans = smalls[i+1].select("span")
                if spans:
                    info_obj.referee = spans[0].text.strip().replace("\xa0", " ")
                break
    except Exception as e:
        print(f"referee alınamadı: {e}")
        info_obj.referee = None

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
        info_obj.home_goals = scores[0].text.strip()
        info_obj.away_goals = scores[1].text.strip()
    except Exception as e:
        print(f"skorlar alınamadı: {e}")
        info_obj.home_goals = None
        info_obj.away_goals = None

    # Home goal scorers
    try:
        goals_html = scorebox.select("div[class='event']")
        home_goals_html = goals_html[0].select("div")
        info_obj.home_goal_scorers = goal_list_crator(home_goals_html)
    except Exception as e:
        print(f"home_goal_scorers alınamadı: {e}")
        info_obj.home_goal_scorers = None

    # Away goal scorers
    try:
        goals_html = scorebox.select("div[class='event']")
        away_goals_html = goals_html[1].select("div")
        info_obj.away_goal_scorers = goal_list_crator(away_goals_html)
    except Exception as e:
        print(f"away_goal_scorers alınamadı: {e}")
        info_obj.away_goal_scorers = None

    return info_obj

async def main():

    browser = await uc.start(headless=False)
    url = "https://fbref.com/en/matches/675b328b/Argentina-Cabo-Verde-July-3-2026-World-Cup"
    page = await browser.get(url)
    result = await scrapper(page, url)
    browser.stop()
    print(result)
if __name__ == "__main__":

    uc.loop().run_until_complete(main())
