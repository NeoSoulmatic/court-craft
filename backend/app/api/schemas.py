from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    abbreviation: str
    full_name: str
    city: str
    nickname: str
    conference: str | None
    division: str | None


class PlayerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    team_id: int | None
    team_abbreviation: str | None = None
    position: str | None
    height: str | None = None
    weight: int | None = None
    is_active: bool


class GameOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    season: str
    game_date: date
    game_datetime_utc: datetime | None
    home_team_id: int
    away_team_id: int
    home_score: int | None
    away_score: int | None
    status: str
    home_team: TeamOut | None = None
    away_team: TeamOut | None = None


class DraftPickOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    season: str
    round: int
    pick_overall: int
    team_id: int | None
    player_id: int | None
    player_name: str
    college: str | None


class HealthOut(BaseModel):
    status: str
    seasons_configured: list[str]


class PredictionOut(BaseModel):
    game_id: str
    home_win_prob: float
    predicted_home_score: float
    predicted_away_score: float
    predicted_spread: float  # home perspective (negative = home favored)
    predicted_total: float
    model_version: str
    note: str = "Placeholder — train model in ml/ to enable live predictions"
