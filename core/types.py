from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Literal



class goal_info(BaseModel):
    # General goal information
    scored_by: str | None = None
    asist_by: str | None = None
    minutes: str | None = None

    # Which side scored
    home_or_away: Literal["home", "away"] | None = None

    # Goal type
    isPenalty: bool | None = False
    isOwnGoal: bool | None = False

class player_info(BaseModel):
    player_name: str | None = None
    player_number: str | None = None

class card_event(BaseModel):
    player_name: str | None = None
    minutes: str | None = None
    card_type: Literal["yellow_card", "red_card"] | None = None
    red_type: Literal["direct", "two_yellow"] | None = None

class substitution(BaseModel):
    player_enter: str | None = None
    player_exit: str | None = None
    minutes: str | None = None

class miss_penalty(BaseModel):
    player_name: str | None = None
    minutes: str | None = None

class team_stats(BaseModel):
    home_name: str | None = None
    away_name: str | None = None

    home_possession: str | None = None
    away_possession: str | None = None

    home_shots: str | None = None
    away_shots: str | None = None

    home_shots_on_target: str | None = None
    away_shots_on_target: str | None = None

    home_missed_shots: str | None = None
    away_missed_shots: str | None = None

    home_saves: str | None = None
    away_saves: str | None = None

    home_yellow_cards: str | None = None
    away_yellow_cards: str | None = None

    home_red_cards: str | None = None
    away_red_cards: str | None = None

    home_fouls: str | None = None
    away_fouls: str | None = None

    home_corners: str | None = None
    away_corners: str | None = None

    home_crosses: str | None = None
    away_crosses: str | None = None

    home_interceptions: str | None = None
    away_interceptions: str | None = None

    home_offsides: str | None = None
    away_offsides: str | None = None

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

    # Team information
    home_name: str | None = None
    away_name: str | None = None

    # Managers and referee
    home_manager: str | None = None
    away_manager: str | None = None
    referee: str | None = None

    # Captains
    home_captain: str | None = None
    away_captain: str | None = None

    # Score infromations
    home_goals: str | None = None
    away_goals: str | None = None

    # Goalscorers info
    home_goal_scorers: list[goal_info] | None = None
    away_goal_scorers: list[goal_info] | None = None

