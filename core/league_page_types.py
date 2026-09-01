from pydantic import BaseModel, ConfigDict


class TableRow(BaseModel):
    model_config = ConfigDict(extra="allow")

class LeagueInfo(BaseModel):
    comp_id: str | None = None
    competition_name: str | None = None
    season: str | None = None

class StandingsTable(BaseModel):
    phase: str | None = None
    column_descriptions: dict[str, str] | None = None
    rows: list[TableRow] | None = None

class LeaguePage(BaseModel):
    model_config = ConfigDict(extra="allow")
    league_info: LeagueInfo | None = None
    standings: list[StandingsTable] | None = None
    standings_home_away: list[TableRow] | None = None
    fixtures: list[TableRow] | None = None
    match_urls: list[str] | None = None
