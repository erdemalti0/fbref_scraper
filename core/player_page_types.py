from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from core.match_report_types import PlayerStats

class PlayerInfo(BaseModel):
    player_id: str | None = None
    player_name: str | None = None
    player_full_name: str | None = None
    player_birth_date: datetime | None = None
    player_born_place: str | None = None
    player_national_team: str | None = None
    player_other_national_team: str | None = None
    player_position: str | None = None
    player_height: int | None = None
    player_weight: int | None = None


class AllStats(BaseModel, extra="allow"):
    standard_stats: list[PlayerStats] | None = None
    standard_stats_col_descriptions: dict | None = None