import os
import argparse
from dotenv import load_dotenv
import nodriver as uc

from scrapers.match_report.match_report_main import scrape_match_report
from scrapers.player_page.player_page_main import scrape_player_page
from scrapers.club_page_by_season.club_page_main import scrape_club_page
from scrapers.league_page.league_page_main import scrape_league_page

load_dotenv()
load_dotenv(".env.local", override=True)

SCRAPERS = {
    "match": (scrape_match_report, "/matches/"),
    "player": (scrape_player_page, "/players/"),
    "club": (scrape_club_page, "/squads/"),
    "league": (scrape_league_page, "/comps/"),
}


TRUE_VALUES = ("1", "true", "yes", "y")
FALSE_VALUES = ("0", "false", "no", "n")


def str2bool(v):
    if v is None:
        return None
    s = str(v).lower()
    if s in TRUE_VALUES:
        return True
    if s in FALSE_VALUES:
        return False
    raise argparse.ArgumentTypeError(f"expected true/false, got: {v!r}")

def main():
    parser = argparse.ArgumentParser(description="fbref.com data scraper")
    parser.add_argument("type", choices=SCRAPERS.keys(), help="page type to scrape")
    parser.add_argument("url", help="fbref.com page URL")
    parser.add_argument("--headless", nargs="?", default=None, const=True,
                        type=str2bool, help="true/false, if omitted the HEADLESS value from .env is used")
    parser.add_argument("--storage_type", type=lambda s: s.lower().strip(),
                        choices=["json", "postgresql", "both"], default=None)
    args = parser.parse_args()

    if "fbref.com" not in args.url:
        parser.error("URL must be a fbref.com address")

    scrape_func, expected_path = SCRAPERS[args.type]
    if expected_path not in args.url:
        parser.error(f"URL for type '{args.type}' must contain '{expected_path}'")

    if args.headless is None:
        headless = str(os.getenv("HEADLESS", "false")).lower().strip() in TRUE_VALUES
    else:
        headless = args.headless

    if args.storage_type is not None:
        storage_type = args.storage_type
    else:
        storage_type = (os.getenv("STORAGE_TYPE", "json") or "json").lower().strip()

    if storage_type not in ("json", "postgresql", "both"):
        parser.error("Invalid storage type")

    uc.loop().run_until_complete(scrape_func(args.url, headless, storage_type))


if __name__ == "__main__":
    main()
