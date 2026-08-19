from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Literal



class goal_info(BaseModel):
    # General goal information
    scored_by: str | None = None
    minutes: str | None = None
    asist_by: str | None = None

    # Which side scored
    home_or_away: Literal["home", "away"] | None = None

    # Goal type
    isPenalty: bool | None = None
    isOwnGoal: bool | None = None

class player_info(BaseModel):
    player_name: str | None = None
    player_number: str | None = None

class card_event(BaseModel):
    card_type: Literal["yellow", "red"] | None = None
    red_type: Literal["direct", "two_yellow"] | None = None
    player_name: str | None = None
    minutes: str | None = None

class substitution(BaseModel):
    player_name_enter: str | None = None
    player_name_exit: str | None = None
    minutes: str | None = None

class events(BaseModel):
    home_events: list | None = None
    away_events: list | None = None

class match_squad(BaseModel):
    home_lineup: str | None = None
    away_lineup: str | None = None

    home_first_eleven: list[player_info] | None = None
    home_bench: list[player_info] | None = None

    away_first_eleven: list[player_info] | None = None
    away_bench: list[player_info] | None = None

class general_match_info(BaseModel):
    match_id: str | None = None
    league: str | None = None
    match_place: str | None = None
    match_date: str | None = None
    attandance: str | None = None

    # Team informations
    home_name: str | None = None
    away_name: str | None = None

    # Managers and referee
    home_manager: str | None = None
    away_manager: str | None = None
    referee: str | None = None

    # Captains
    home_captain: str | None = None
    away_captain: str | None = None

    #Score infromations
    home_goals: str | None = None
    away_goals: str | None = None

    #Goal scorers info
    home_goal_scorers: list[goal_info] | None = None
    away_goal_scorers: list[goal_info] | None = None

