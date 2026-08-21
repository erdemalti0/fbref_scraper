from pydantic import BaseModel, ConfigDict
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


class AllStats(BaseModel):
    model_config = ConfigDict(extra="allow")

class PlayerPage(BaseModel):
    info: PlayerInfo | None = None
    all_stats: AllStats | None = None