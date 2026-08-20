from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Literal


class GoalInfo(BaseModel):
    # General goal information
    scorer: str | None = None
    assist_provider: str | None = None
    minute: str | None = None

    # Goal type
    is_penalty: bool = False
    is_own_goal: bool = False

class PlayerInfo(BaseModel):
    name: str | None = None
    number: int | None = None

class CardEvent(BaseModel):
    player_name: str | None = None
    minute: str | None = None
    card_type: Literal["yellow_card", "red_card"] | None = None
    red_type: Literal["direct", "two_yellow"] | None = None

class Substitution(BaseModel):
    player_in: str | None = None
    player_out: str | None = None
    minute: str | None = None

class MissedPenalty(BaseModel):
    player_name: str | None = None
    minute: str | None = None

class PlayerStats(BaseModel, extra="allow"):
    player: str | None = None

class MatchPlayerStats(BaseModel):
    home_stats: list[PlayerStats] | None = None
    away_stats: list[PlayerStats] | None = None

    home_goalkeeper_stats: list[PlayerStats] | None = None
    away_goalkeeper_stats: list[PlayerStats] | None = None

class TeamStats(BaseModel):
    home_name: str | None = None
    away_name: str | None = None

    home_possession: str | None = None
    away_possession: str | None = None

    home_shots: int | None = None
    away_shots: int | None = None

    home_shots_on_target: int | None = None
    away_shots_on_target: int | None = None

    home_missed_shots: int | None = None
    away_missed_shots: int | None = None

    home_saves: int | None = None
    away_saves: int | None = None

    home_yellow_cards: int | None = None
    away_yellow_cards: int | None = None

    home_red_cards: int | None = None
    away_red_cards: int | None = None

    home_fouls: int | None = None
    away_fouls: int | None = None

    home_corners: int | None = None
    away_corners: int | None = None

    home_crosses: int | None = None
    away_crosses: int | None = None

    home_interceptions: int | None = None
    away_interceptions: int | None = None

    home_offsides: int | None = None
    away_offsides: int | None = None

class Events(BaseModel):
    home_events: list[GoalInfo | CardEvent | Substitution | MissedPenalty] | None = None
    away_events: list[GoalInfo | CardEvent | Substitution | MissedPenalty] | None = None

class MatchSquad(BaseModel):
    home_formation: str | None = None
    away_formation: str | None = None

    home_starting_eleven: list[PlayerInfo] | None = None
    home_bench: list[PlayerInfo] | None = None

    away_starting_eleven: list[PlayerInfo] | None = None
    away_bench: list[PlayerInfo] | None = None

class GeneralMatchInfo(BaseModel):
    match_id: str | None = None
    league: str | None = None
    venue: str | None = None
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
