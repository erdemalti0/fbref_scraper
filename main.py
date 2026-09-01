import argparse

import nodriver as uc

from scrapers.match_report.match_report_main import scrape_match_report
from scrapers.player_page.player_page_main import scrape_player_page
from scrapers.club_page_by_season.club_page_main import scrape_club_page
from scrapers.league_page.league_page_main import scrape_league_page

SCRAPERS = {
    "match": (scrape_match_report, "/matches/"),
    "player": (scrape_player_page, "/players/"),
    "club": (scrape_club_page, "/squads/"),
    "league": (scrape_league_page, "/comps/"),
}


def main():
    parser = argparse.ArgumentParser(description="fbref.com veri kazıyıcı")
    parser.add_argument("type", choices=SCRAPERS.keys(), help="kazınacak sayfa tipi")
    parser.add_argument("url", help="fbref.com sayfa linki")
    args = parser.parse_args()

    if "fbref.com" not in args.url:
        parser.error("link fbref.com adresi olmalı")

    scrape_func, expected_path = SCRAPERS[args.type]
    if expected_path not in args.url:
        parser.error(f"{args.type} tipi için link '{expected_path}' içermeli")

    uc.loop().run_until_complete(scrape_func(args.url))


if __name__ == "__main__":
    main()
