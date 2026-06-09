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
    season_type: str = "Regular Season"
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


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_date: date
    season: str
    transaction_type: str
    description: str
    source: str


class HealthOut(BaseModel):
    status: str
    seasons_configured: list[str]


class MarketMetricOut(BaseModel):
    games: int | None = None
    games_with_odds: int | None = None
    accuracy: float | None = None
    hit_rate: float | None = None
    model_pick_hit_rate: float | None = None
    model_over_hit_rate: float | None = None
    vegas_baseline_over_50: float | None = None
    vegas_over_rate: float | None = None
    note: str | None = None


class ModelBacktestOut(BaseModel):
    model_version: str
    train_seasons: list[str]
    test_season: str
    regular_season_only: bool
    moneyline: MarketMetricOut
    spread: MarketMetricOut
    total: MarketMetricOut
    errors: dict[str, float]
    odds_source: str
    odds_coverage_note: str


class PredictionOut(BaseModel):
    game_id: str
    game_date: date | None = None
    season_type: str = "Regular Season"
    home_team: str | None = None
    away_team: str | None = None
    home_win_prob: float
    predicted_home_score: float
    predicted_away_score: float
    predicted_spread: float  # home perspective (negative = home favored)
    predicted_total: float
    model_version: str
    note: str | None = None
    # Live market (The Odds API)
    market_available: bool = False
    market_bookmaker: str | None = None
    market_home_moneyline: int | None = None
    market_away_moneyline: int | None = None
    market_home_implied_prob: float | None = None
    market_away_implied_prob: float | None = None
    market_spread_home: float | None = None
    market_total: float | None = None
    ml_pick_side: str | None = None
    ml_edge: float | None = None
    ml_quarter_kelly_pct: float | None = None
    spread_pick_side: str | None = None
    spread_cover_prob_model: float | None = None
    spread_cover_prob_market: float | None = None
    spread_edge: float | None = None
    spread_quarter_kelly_pct: float | None = None
    total_pick_side: str | None = None
    total_win_prob_model: float | None = None
    total_win_prob_market: float | None = None
    total_edge: float | None = None
    total_quarter_kelly_pct: float | None = None
    odds_fetched_at: str | None = None
    odds_requests_remaining: int | None = None
    odds_stale: bool = False
    odds_hint: str | None = None


class OddsStatusOut(BaseModel):
    configured: bool
    cache_path: str
    fetched_at: str | None = None
    requests_remaining: int | None = None
    event_count: int = 0
    stale: bool = False
    error: str | None = None
    signup_url: str
    budget_note: str
