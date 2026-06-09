from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.schemas import DraftPickOut, GameOut, HealthOut, PlayerOut, PredictionOut, TeamOut
from app.core.config import get_settings
from app.core.database import get_db
from app.models.draft import DraftPick
from app.models.game import Game
from app.models.player import Player
from app.models.team import Team

router = APIRouter()


@router.get("/health", response_model=HealthOut)
async def health() -> HealthOut:
    settings = get_settings()
    return HealthOut(status="ok", seasons_configured=settings.seasons_list)


@router.get("/teams", response_model=list[TeamOut])
async def list_teams(db: AsyncSession = Depends(get_db)) -> list[Team]:
    result = await db.execute(select(Team).order_by(Team.full_name))
    return list(result.scalars().all())


@router.get("/teams/{team_id}", response_model=TeamOut)
async def get_team(team_id: int, db: AsyncSession = Depends(get_db)) -> Team:
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.get("/players", response_model=list[PlayerOut])
async def list_players(
    db: AsyncSession = Depends(get_db),
    team_id: int | None = Query(default=None),
    active_only: bool = Query(default=True),
    limit: int = Query(default=100, le=500),
) -> list[Player]:
    stmt = select(Player).order_by(Player.full_name).limit(limit)
    if team_id is not None:
        stmt = stmt.where(Player.team_id == team_id)
    if active_only:
        stmt = stmt.where(Player.is_active.is_(True))
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/players/{player_id}", response_model=PlayerOut)
async def get_player(player_id: int, db: AsyncSession = Depends(get_db)) -> Player:
    player = await db.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/games", response_model=list[GameOut])
async def list_games(
    db: AsyncSession = Depends(get_db),
    season: str | None = Query(default=None),
    game_date: date | None = Query(default=None),
    limit: int = Query(default=50, le=200),
) -> list[Game]:
    stmt = (
        select(Game)
        .options(selectinload(Game.home_team), selectinload(Game.away_team))
        .order_by(Game.game_date.desc())
        .limit(limit)
    )
    if season:
        stmt = stmt.where(Game.season == season)
    if game_date:
        stmt = stmt.where(Game.game_date == game_date)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/games/{game_id}", response_model=GameOut)
async def get_game(game_id: str, db: AsyncSession = Depends(get_db)) -> Game:
    stmt = (
        select(Game)
        .options(selectinload(Game.home_team), selectinload(Game.away_team))
        .where(Game.id == game_id)
    )
    result = await db.execute(stmt)
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.get("/draft", response_model=list[DraftPickOut])
async def list_draft_picks(
    db: AsyncSession = Depends(get_db),
    season: str | None = Query(default=None),
    limit: int = Query(default=60, le=300),
) -> list[DraftPick]:
    stmt = select(DraftPick).order_by(DraftPick.season.desc(), DraftPick.pick_overall).limit(limit)
    if season:
        stmt = stmt.where(DraftPick.season == season)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/predictions/upcoming", response_model=list[PredictionOut])
async def upcoming_predictions(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=10, le=30),
) -> list[PredictionOut]:
    """Placeholder predictions until ML pipeline is trained."""
    stmt = (
        select(Game)
        .where(Game.status == "scheduled")
        .order_by(Game.game_date)
        .limit(limit)
    )
    result = await db.execute(stmt)
    games = list(result.scalars().all())

    return [
        PredictionOut(
            game_id=game.id,
            home_win_prob=0.5,
            predicted_home_score=110.0,
            predicted_away_score=108.0,
            predicted_spread=-2.0,
            predicted_total=218.0,
            model_version="placeholder",
        )
        for game in games
    ]
