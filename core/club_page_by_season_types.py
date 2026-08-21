from pydantic import BaseModel, ConfigDict


class CompetitionUrl(BaseModel):
    competition_name: str | None = None
    competition_url: str | None = None

class ClubInfo(BaseModel):
    club_id: str | None = None
    club_name: str | None = None
    country_name: str | None = None
    season: str | None = None
