from core.match_report_types import PlayerStats
from core.club_page_by_season_types import FixtureRow
from core.logger import get_logger
from typing import Literal
import re

logger = get_logger(__name__)

def parse_cell_value(text: str):
    if not text:
        return None
    cleaned = text.replace(",", "")
    if cleaned.isdigit():
        return int(cleaned)
    try:
        return float(cleaned)
    except ValueError:
        return text

def column_name_scraper(content) -> list:

    names = []
    try:
        for column in content.select('th'):
            col_name = column.text.strip().replace(" ", "_").lower()
            if col_name == "" or not col_name:
                col_name = "no_name_col"

            if col_name == "matches" or col_name == "match_report" or col_name == "match":
                names.append({
                    "column_name": "",
                    "column_description": None,
                })
                continue

            col_description = None

            try:
                data_tip_content = column.get("data-tip", "")
                match = re.search(r"<strong>(.*?)</strong>", data_tip_content)
                column_description = match.group(1).strip().replace(" ", "_").lower() if match else None

                col_description = column_description
            except Exception as e:
                logger.warning(f"Column description could not be parsed: {e}")

            col_obj = {
                "column_name": col_name,
                "column_description": col_description,
            }

            names.append(col_obj)

    except Exception as e:
        logger.warning(f"Column names could not be scraped: {e}")

    return names

def row_scraper(content, columns, model_cls=PlayerStats) -> list:

    result = []
    first_col_name = columns[0]["column_name"].strip().lower() if columns else ""
    for row in content:
        all_cels = row.find_all(["th", "td"])
        if not all_cels or not any(cel.text.strip() for cel in all_cels):
            continue
        if first_col_name and all_cels[0].text.strip().lower() == first_col_name:
            continue
        stats = model_cls()
        for i, cel in enumerate(all_cels):
            if i == len(columns):
                break
            var_name = columns[i]["column_name"].strip().lower()
            if var_name:
                setattr(stats, var_name, parse_cell_value(cel.text.strip()))

        result.append(stats)

    return result

def column_description_mapper(columns) -> dict[str, str]:
    return {
        col["column_name"].strip().lower(): col["column_description"]
        for col in columns
        if col["column_name"].strip() and col["column_description"]
    }

def table_scraper(content, table_name, obj, return_type: Literal["player", "fixture"] = "player"):
    if content:
        try:
            cols = content.select_one("thead").select("tr")
            if len(cols) == 1:
                column_names = column_name_scraper(cols[0])
            else:
                column_names = column_name_scraper(cols[-1])
        except Exception as e:
            column_names = None
            logger.warning(f"Table header could not be scraped for '{table_name}': {e}")

        if column_names:
            try:
                rows = content.select_one("tbody").select("tr")
                column_descriptions = column_description_mapper(column_names)
                setattr(obj, table_name+"_col_descriptions", column_descriptions)
            except Exception as e:
                rows = None
                logger.warning(f"Table body could not be scraped for '{table_name}': {e}")

            if rows:
                try:
                    if return_type.lower() == "player":
                        result = row_scraper(rows, column_names, PlayerStats)
                    elif return_type.lower() == "fixture":
                        result = row_scraper(rows, column_names, FixtureRow)
                    else:
                        result = row_scraper(rows, column_names)

                    setattr(obj, table_name, result)
                except Exception as e:
                    logger.warning(f"Rows could not be scraped for '{table_name}': {e}")

        tfoot_html = content.select_one("tfoot")
        if tfoot_html:
            trs = tfoot_html.select("tr")
        else:
            return


        if len(trs) > 2:
            trs = trs[1::]

            temp = []
            for tr in trs:
                if set(tr.get("class", [])) == {"spacer", "partial_table"}:
                    continue
                temp.append(tr)

            trs = temp
            try:
                column_names = column_name_scraper(trs[0])
            except Exception as e:
                column_names = None
                logger.warning(f"Footer column names could not be scraped for '{table_name}': {e}")
            if column_names:
                try:
                    rows = trs[1::]
                except Exception as e:
                    rows = None
                    logger.warning(f"Footer rows could not be scraped for '{table_name}': {e}")

                if rows:
                    try:
                        result = row_scraper(rows, column_names)
                        setattr(obj, table_name+"_by_club_and_league", result)
                    except Exception as e:
                        logger.warning(f"Footer table could not be scraped for '{table_name}': {e}")