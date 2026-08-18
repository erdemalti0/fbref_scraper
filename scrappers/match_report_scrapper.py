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

    try:
        print("Scrapping: " + url)
        await page.wait_for('div.scorebox')
    except Exception:
        RuntimeError(f"Sayfa alınamadı {url}")

    print("Scrapping başarılı")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, 'html.parser')

    scorebox = soup.find('div', class_='scorebox')

    if scorebox:
        #match_info = general_match_info()
        try:
            match_id = url.split("/")[5]
            score_box_meta_html = soup.select_one('div[class="scorebox_meta"]')
            if score_box_meta_html:
                # Get date data
                data = score_box_meta_html.select_one('a[href*="/matches/"]').text.strip().replace(",", "").split(" ")
                match_date = f"{data[2]}/{data[1]}/{data[-1]}"

                # Get league
                league = score_box_meta_html.select_one('a[href*="/comps/"]').text.strip()

                # Get smalls elements for referee and place information
                smalls = score_box_meta_html.select("small")

                # Place and referee information in smalls we find them in a loop
                for i, small in enumerate(smalls):
                    if i == 1:
                        match_place = small.text.strip()
                    elif i == 3:
                        spans = small.select("span")
                        if spans:
                            referee = spans[0].text.strip().replace("\xa0", " ")
        except Exception as e:
            raise RuntimeError(f"Scrapping başarısız: {url}\n{e}")

        print(f"Batch 1 başarılı devam ediliyor.")

        try:
            home_team_html = scorebox.find('div', id='sb_team_0')
            away_team_html = scorebox.find('div', id='sb_team_1')
            if home_team_html:
                home_name = home_team_html.select_one("a[href*='/squads/']").text.strip()

                # Datapoint is a class in this html code there is a 2 datapoint one of it
                # give us a manager information other one captain
                datapoints = home_team_html.select('div[class="datapoint"]')
                home_manager = datapoints[0].text.strip().replace("Manager: ", "").replace("\xa0", " ")
                home_captain = datapoints[1].select_one("a").text.strip().replace("\xa0", " ")

            if away_team_html:
                away_name = away_team_html.select_one("a[href*='/squads/']").text.strip()

                datapoints = away_team_html.select('div[class="datapoint"]')
                away_manager = datapoints[0].text.strip().replace("Manager: ", "").replace("\xa0", " ")
                away_captain = datapoints[1].select_one("a").text.strip().replace("\xa0", " ")

            scores = soup.find_all("div", class_="score")
            if scores:
                home_goals = scores[0].text.strip()
                away_goals = scores[1].text.strip()

            home_goals_list = []
            goals_html = scorebox.select("div[class='event']")
            if goals_html:
                home_goals_html = goals_html[0].select("div")
                away_goals_html = goals_html[1].select("div")

                home_goals_list = goal_list_crator(home_goals_html)
                away_goals_list = goal_list_crator(away_goals_html)

        except Exception as e:
            raise RuntimeError(f"Scrapping başarısız: {url}\n{e}")


        info_obj = general_match_info(
            match_id = match_id,
            league = league,
            match_place = match_place,
            match_date = match_date,
            home_name = home_name,
            away_name = away_name,
            home_manager = home_manager,
            away_manager = away_manager,
            home_captain = home_captain,
            away_captain = away_captain,
            home_goals = home_goals,
            away_goals = away_goals,
            home_goal_scorers = home_goals_list,
            away_goal_scorers = away_goals_list,
            referee = referee,
        )

        return info_obj

async def main():

    browser = await uc.start(headless=False)
    url = "https://fbref.com/en/matches/91a56b43/Genclerbirligi-Fenerbahce-August-15-2026-Super-Lig"
    page = await browser.get(url)
    result = await scrapper(page, url)
    browser.stop()
    print(result)
if __name__ == "__main__":

    uc.loop().run_until_complete(main())
