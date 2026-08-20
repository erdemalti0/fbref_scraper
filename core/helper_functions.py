from bs4 import BeautifulSoup
from core.player_page_types import *
from core.match_report_types import *
import re

def parse_cell_value(text: str):
    if not text:
        return None
    if text.isdigit():
        return int(text)
    try:
        return float(text)
    except ValueError:
        return text

def column_name_scraper(content) -> list:

    names = []
    try:
        for column in content.select('th'):
            col_name = column.text.strip().replace(" ", "_").lower()
            if col_name == "" or not col_name:
                col_name = "no_name_col"

            col_description = None

            try:
                data_tip_content = column.get("data-tip", "")
                match = re.search(r"<strong>(.*?)</strong>", data_tip_content)
                column_description = match.group(1).strip().replace(" ", "_").lower() if match else None

                col_description = column_description
            except Exception as e:
                print(f"Column description error: {e}")

            col_obj = {
                "column_name": col_name,
                "column_description": col_description,
            }

            names.append(col_obj)

    except Exception as e:
        print(f"Kolon isimleri alınamadı")
    try:
        if names and names[-1]["column_name"] == "matches":
            names.pop(-1)
    except Exception as e:
        print(f"Matches error: {e}")

    return names

def row_scraper(content, columns) -> list[PlayerStats]:

    result = []
    for row in content:
        stats = PlayerStats()
        all_cels = row.find_all(["th", "td"])
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

def table_scraper(content, table_name, obj):
    if content:
        try:
            column_names = column_name_scraper(content.select_one("thead").select("tr")[1])
        except Exception as e:
            column_names = None
            print(f"Standard stats alınamadı {e}")

        if column_names:
            try:
                rows = content.select_one("tbody").select("tr")
                column_descriptions = column_description_mapper(column_names)
                setattr(obj, table_name+"_col_descriptions", column_descriptions)
            except Exception as e:
                rows = None
                print(e)

            if rows:
                try:
                    result = row_scraper(rows, column_names)
                    setattr(obj, table_name, result)
                except Exception as e:
                    print("Satır alınamadı")

        tfoot_html = content.select_one("tfoot")
        trs = tfoot_html.select("tr")

        if len(trs) > 1:
            trs = trs[1::]

            temp = []
            for tr in trs:
                if tr.get("class", "") == ["spacer", "partial_table"]:
                    continue
                temp.append(tr)

            trs = temp
            try:
                column_names = column_name_scraper(trs[0])
            except Exception as e:
                column_names = None
                pass
            if column_names:
                try:
                    rows = trs[1::]
                except Exception as e:
                    rows = None
                    print(f"Satırlar alınamadı {e}")

                if rows:
                    try:
                        result = row_scraper(rows, column_names)
                        setattr(obj, table_name+"_by_club_and_league", result)
                    except Exception as e:
                        print("Tablo alınamadı")