import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.player_page_types import AllStats
from core.browser import start_browser
from scrapers.match_report.match_player_stats_scraper import column_name_scraper
from scrapers.match_report.match_player_stats_scraper import column_description_mapper
from scrapers.match_report.match_player_stats_scraper import row_scraper

async def all_stats_scraper(page):
    stats = AllStats()
    try:
        print(f"Oyuncu verileri alınıyor")
        await page.select('div[id*="stats_player_summary_"]')
    except Exception as e:
        print(f"Oyuncu verileri alınamadı {e}")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    standard_stats_html = soup.select_one('table[id="stats_standard_dom_lg"]')

    if standard_stats_html:

        try:
            standard_column_names = column_name_scraper(standard_stats_html.select_one("thead").select("tr")[1])
        except Exception as e:
            standard_column_names = None
            print(f"Standard stats alınamadı {e}")

        if standard_column_names:
            try:
                rows = standard_stats_html.select_one("tbody").select("tr")
                column_descriptions = column_description_mapper(rows)
                stats.standard_stats_col_descriptions = column_descriptions
            except Exception as e:
                rows = None
                print(e)

            if rows:
                try:
                    result = row_scraper(rows, standard_column_names)
                    stats.standard_stats = result
                except Exception as e:
                    print("Satır alınamadı")



async def main():
    browser = await start_browser(headless=False)
    try:
        url = "https://fbref.com/en/players/e6af3cc7/Clarence-Seedorf"

        page = await browser.get(url)
        await all_stats_scraper(page)
    finally:
        browser.stop()

if "__main__" == __name__:

    uc.loop().run_until_complete(main())