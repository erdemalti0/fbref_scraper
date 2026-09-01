import sys
import re
from bs4 import BeautifulSoup
import nodriver as uc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.league_page_types import LeagueInfo
from core.logger import get_logger

logger = get_logger(__name__)

async def league_info_scraper(page, url) -> LeagueInfo:
    info = LeagueInfo()

    try:
        id_match = re.search(r"/comps/(\d+)", url)
        info.comp_id = id_match.group(1) if id_match else None
    except Exception as e:
        logger.warning(f"comp_id could not be parsed: {e}")

    html_content = await page.get_content()
    soup = BeautifulSoup(html_content, "html.parser")

    h1 = soup.select_one("h1")
    if h1:
        head_span = h1.select_one("span")
        texts = head_span.text.strip().split(" ") if head_span else [t for t in h1.text.split() if t]
        try:
            info.season = texts[0]
        except Exception as e:
            logger.warning(f"Season could not be parsed: {e}")

        try:
            info.competition_name = " ".join(texts[1:texts.index("Stats")]) if "Stats" in texts else " ".join(texts[1:])
        except Exception as e:
            logger.warning(f"Competition name could not be parsed: {e}")

    return info

async def main():
    browser = await start_browser()
    try:
        url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        page = await browser.get(url)

        info = await league_info_scraper(page, url)
        print(info)
    finally:
        browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
