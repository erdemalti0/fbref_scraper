import asyncio
import json
import sys
from pathlib import Path

import nodriver as uc

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.browser import start_browser
from core.types import MatchReport
from scrapers.match_report.match_report_scraper import match_general_info_scraper
from scrapers.match_report.match_team_stats_scraper import team_stats_scrapper
from scrapers.match_report.match_event_scraper import match_events_scraper
from scrapers.match_report.match_squad_scraper import match_squad_scraper
from scrapers.match_report.match_player_stats_scraper import player_stats_scraper

STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage"


async def scrape_page(page, url: str) -> MatchReport:
    try:
        await page.wait_for('div[id="footer"]')
    except Exception:
        raise RuntimeError(f"Sayfa tam yüklenemedi {url}")

    report = MatchReport()

    scrapers = [
        ("general_info", match_general_info_scraper(page, url)),
        ("team_stats", team_stats_scrapper(page)),
        ("events", match_events_scraper(page)),
        ("squad", match_squad_scraper(page)),
        ("player_stats", player_stats_scraper(page)),
    ]

    for name, coro in scrapers:
        try:
            setattr(report, name, await coro)
        except Exception as e:
            print(f"{name} alınamadı ({url}): {e}")

    return report


def save_report(report: MatchReport) -> Path | None:
    match_id = report.general_info.match_id if report.general_info else None
    if not match_id:
        print("match_id bulunamadı, rapor kaydedilmedi")
        return None

    STORAGE_DIR.mkdir(exist_ok=True)
    path = STORAGE_DIR / f"{match_id}.json"
    path.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Rapor kaydedildi: {path}")
    return path


async def scrape_match_report(url: str, headless: bool = False) -> MatchReport:
    browser = await start_browser(headless=headless)
    try:
        page = await browser.get(url)
        report = await scrape_page(page, url)
        save_report(report)
        return report
    finally:
        browser.stop()


async def scrape_many(urls: list[str], headless: bool = False, delay: float = 3.0) -> list[MatchReport]:
    browser = await start_browser(headless=headless)
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
                print(f"Maç alınamadı ({url}): {e}")

        return reports
    finally:
        browser.stop()


async def main():
    url = "https://fbref.com/en/matches/675b328b/Argentina-Cabo-Verde-July-3-2026-World-Cup"
    report = await scrape_match_report(url, headless=False)
    print(report)


if __name__ == "__main__":
    uc.loop().run_until_complete(main())
