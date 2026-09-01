import sys
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.club_page_by_season_types import CompetitionUrl
from core.logger import get_logger

logger = get_logger(__name__)

async def competition_url_scraper(page, url) -> list[CompetitionUrl] | None :

    try:
        logger.info("Scraping competition urls")
        await page.wait_for('div[class="filter"]')
    except Exception as e:
        logger.warning(f"Competition filter section could not be loaded: {e}")
        return None

    result = []
    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, 'html.parser')

    filter_ = soup.select_one('div[class="filter"]')
    if filter_:
        divs = filter_.select('div')
        try:
            for div in divs:
                a = div.select_one('a')
                if a and a.get('href'):
                    aurl = a.get('href').strip()
                    if not aurl.startswith('https://fbref.com'):
                        aurl = "https://fbref.com" + aurl
                    obj = CompetitionUrl(
                        competition_name=a.text.strip(),
                        competition_url=aurl,
                    )
                else:
                    obj = CompetitionUrl(
                        competition_name=div.text.strip(),
                        competition_url=None
                    )

                result.append(obj)
        except Exception as e:
            logger.warning(f"Competition urls could not be parsed: {e}")

        return result

async def main():
    browser = await start_browser()
    try:
        url = "https://fbref.com/en/squads/18bb7c10/2025-2026/Arsenal-Stats"
        page = await browser.get(url)
        await competition_url_scraper(page, url)
    except Exception as e:
        logger.error(f"Competition urls could not be scraped: {e}")
    finally:
        browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())