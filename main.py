import sys

import nodriver as uc

from scrapers.match_report.match_report_main import scrape_match_report
from scrapers.player_page.player_page_main import scrape_player_page
from scrapers.club_page_by_season.club_page_main import scrape_club_page


def main():
    if len(sys.argv) < 3:
        print("Kullanım: python main.py <match|player|club> <url>")
        return

    report_type = sys.argv[1]
    url = sys.argv[2]

    if report_type == "match":
        coro = scrape_match_report(url)
    elif report_type == "player":
        coro = scrape_player_page(url)
    elif report_type == "club":
        coro = scrape_club_page(url)
    else:
        print(f"Bilinmeyen tip: {report_type} (match | player | club)")
        return

    uc.loop().run_until_complete(coro)


if __name__ == "__main__":
    main()
