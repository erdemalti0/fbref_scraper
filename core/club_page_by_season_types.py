from pydantic import BaseModel, ConfigDict

class FixtureRow(BaseModel, extra="allow"):
    ConfigDict(extra="allow")

class ScoringAndFixture(BaseModel):
    ConfigDict(extra="allow")

class ClubCompetition(BaseModel, extra="allow"):
    ConfigDict(extra="allow")
    competition_name: str | None = None
    scoring_and_fixture: ScoringAndFixture | None = None


class CompetitionUrl(BaseModel):
    competition_name: str | None = None
    competition_url: str | None = None

class ClubInfo(BaseModel):
    club_id: str | None = None
    club_name: str | None = None
    country_name: str | None = None
    season: str | None = None

class ClubPageBySeason(BaseModel):
    ConfigDict(extra="allow")
    club_info: ClubInfo | None = None
    competitions: list[ClubCompetition] | None = None