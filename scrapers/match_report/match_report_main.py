import asyncio
import sys
from pathlib import Path

import nodriver as uc

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.storage import save_json
from core.match_report_types import MatchReport
from core.logger import get_logger
from scrapers.match_report.match_report_scraper import match_general_info_scraper
from scrapers.match_report.match_team_stats_scraper import team_stats_scraper
from scrapers.match_report.match_event_scraper import match_events_scraper
from scrapers.match_report.match_squad_scraper import match_squad_scraper
from scrapers.match_report.match_player_stats_scraper import player_stats_scraper

logger = get_logger(__name__)

STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage"


async def scrape_page(page, url: str) -> MatchReport:
    loaded = False
    for attempt in range(3):
        try:
            await page.wait_for('div[id="footer"]')
            loaded = True
            break
        except Exception:
            await asyncio.sleep(2)
    if not loaded:
        raise RuntimeError(f"Page did not fully load {url}")

    report = MatchReport()

    scrapers = [
        ("general_info", match_general_info_scraper(page, url)),
        ("team_stats", team_stats_scraper(page)),
        ("events", match_events_scraper(page)),
        ("squad", match_squad_scraper(page)),
        ("player_stats", player_stats_scraper(page)),
    ]

    for name, coro in scrapers:
        try:
            setattr(report, name, await coro)
        except Exception as e:
            logger.error(f"Section '{name}' could not be scraped ({url}): {e}")

    return report


def save_report(report: MatchReport) -> Path | None:
    match_id = report.general_info.match_id if report.general_info else None
    return save_json(report, STORAGE_DIR, match_id, "match")


async def scrape_match_report(url: str) -> MatchReport:
    browser = await start_browser()
    try:
        page = await browser.get(url)
        report = await scrape_page(page, url)
        save_report(report)
        return report
    finally:
        browser.stop()


async def scrape_many(urls: list[str], delay: float = 3.0) -> list[MatchReport]:
    browser = await start_browser()
    try:
        reports = []
        for i, url in enumerate(urls):
            if i > 0:
                await asyncio.sleep(delay)

            try:
                page = await browser.get(url)
                report = await scrape_page(page, url)
                save_report(report)
                reports.append(report)
            except Exception as e:
                logger.error(f"Match could not be scraped ({url}): {e}")

        return reports
    finally:
        browser.stop()


async def main():
    url = "https://fbref.com/en/matches/675b328b/Argentina-Cabo-Verde-July-3-2026-World-Cup"
    report = await scrape_match_report(url)
    print(report)


if __name__ == "__main__":
    uc.loop().run_until_complete(main())
