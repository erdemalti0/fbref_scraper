from pydantic import BaseModel, ConfigDict

class FixtureRow(BaseModel):
    model_config = ConfigDict(extra="allow")

class ClubCompetition(BaseModel):
    model_config = ConfigDict(extra="allow")
    competition_name: str | None = None
    scoring_and_fixture: list[FixtureRow] | None = None


class CompetitionUrl(BaseModel):
    competition_name: str | None = None
    competition_url: str | None = None

class ClubInfo(BaseModel):
    club_id: str | None = None
    club_name: str | None = None
    country_name: str | None = None
    season: str | None = None

class ClubPageBySeason(BaseModel):
    model_config = ConfigDict(extra="allow")
    club_info: ClubInfo | None = None
    competitions: list[ClubCompetition] | None = None
