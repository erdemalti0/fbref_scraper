from pydantic import BaseModel, ConfigDict


class ClubInfo(BaseModel):
    club_id: str | None = None
    club_name: str | None = None
    country_name: str | None = None
    season: str | None = None
