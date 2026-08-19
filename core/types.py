from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Literal



class GoalInfo(BaseModel):
    # General goal information
    scored_by: str | None = None
    assist_by: str | None = None
    minutes: str | None = None

    # Goal type
    is_penalty: bool = False
    is_own_goal: bool = False

class PlayerInfo(BaseModel):
    player_name: str | None = None
    player_number: int | None = None

class CardEvent(BaseModel):
    player_name: str | None = None
    minutes: str | None = None
    card_type: Literal["yellow_card", "red_card"] | None = None
    red_type: Literal["direct", "two_yellow"] | None = None

class Substitution(BaseModel):
    player_enter: str | None = None
    player_exit: str | None = None
    minutes: str | None = None

class MissPenalty(BaseModel):
    player_name: str | None = None
    minutes: str | None = None

class TeamStats(BaseModel):
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

class Events(BaseModel):
    home_events: list[GoalInfo | CardEvent | Substitution | MissPenalty] | None = None
    away_events: list[GoalInfo | CardEvent | Substitution | MissPenalty] | None = None

class MatchSquad(BaseModel):
    home_lineup: str | None = None
    away_lineup: str | None = None

    home_first_eleven: list[PlayerInfo] | None = None
    home_bench: list[PlayerInfo] | None = None

    away_first_eleven: list[PlayerInfo] | None = None
    away_bench: list[PlayerInfo] | None = None

class GeneralMatchInfo(BaseModel):
    match_id: str | None = None
    league: str | None = None
    match_place: str | None = None
    match_date: datetime | None = None
    attendance: str | None = None

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

    # Score information
    home_goals: int | None = None
    away_goals: int | None = None

    # Goalscorers info
    home_goal_scorers: list[GoalInfo] | None = None
    away_goal_scorers: list[GoalInfo] | None = None

