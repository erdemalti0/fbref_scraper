from pydantic import BaseModel
from typing import Literal
from datetime import datetime

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

class Season(BaseModel, extra="allow"):
    season: str | None = None

class StandardStats(BaseModel):
    seasons: list[Season] | None = None