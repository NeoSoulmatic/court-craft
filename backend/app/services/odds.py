"""Live odds from The Odds API with file cache and prediction enrichment."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

from app.core.config import get_settings

REPO_ROOT = Path(__file__).resolve().parents[3]
LIVE_CACHE_PATH = REPO_ROOT / "data" / "odds" / "live_cache.json"

ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

# Odds API naming quirks vs nba_api full_name
TEAM_ALIASES = {
    "la clippers": "los angeles clippers",
    "la lakers": "los angeles lakers",
}


def _normalize_team(name: str) -> str:
    key = re.sub(r"\s+", " ", name.strip().lower())
    return TEAM_ALIASES.get(key, key)


def _parse_commence_date(commence_time: str) -> date:
    dt = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
    return dt.astimezone(timezone.utc).date()


def _pick_bookmaker(bookmakers: list[dict]) -> dict | None:
    preferred = ("draftkings", "fanduel", "betmgm", "caesars")
    by_key = {b.get("key"): b for b in bookmakers if b.get("key")}
    for key in preferred:
        if key in by_key:
            return by_key[key]
    return bookmakers[0] if bookmakers else None


def _market_outcomes(bookmaker: dict, market_key: str) -> list[dict]:
    for market in bookmaker.get("markets", []):
        if market.get("key") == market_key:
            return market.get("outcomes", [])
    return []


def _parse_event(event: dict) -> dict | None:
    home = event.get("home_team")
    away = event.get("away_team")
    commence = event.get("commence_time")
    if not home or not away or not commence:
        return None

    bookmaker = _pick_bookmaker(event.get("bookmakers", []))
    if not bookmaker:
        return None

    h2h = _market_outcomes(bookmaker, "h2h")
    spreads = _market_outcomes(bookmaker, "spreads")
    totals = _market_outcomes(bookmaker, "totals")

    home_ml = away_ml = None
    for outcome in h2h:
        if outcome.get("name") == home:
            home_ml = int(outcome["price"])
        elif outcome.get("name") == away:
            away_ml = int(outcome["price"])

    spread_home = spread_home_price = spread_away_price = None
    for outcome in spreads:
        if outcome.get("name") == home and outcome.get("point") is not None:
            spread_home = float(outcome["point"])
            spread_home_price = int(outcome["price"])
        elif outcome.get("name") == away and outcome.get("point") is not None:
            spread_away_price = int(outcome["price"])

    total_line = over_price = under_price = None
    for outcome in totals:
        if outcome.get("name") == "Over" and outcome.get("point") is not None:
            total_line = float(outcome["point"])
            over_price = int(outcome["price"])
        elif outcome.get("name") == "Under" and outcome.get("point") is not None:
            under_price = int(outcome["price"])

    game_date = _parse_commence_date(commence)
    return {
        "event_id": event.get("id"),
        "home_team": home,
        "away_team": away,
        "game_date": game_date.isoformat(),
        "bookmaker": bookmaker.get("key"),
        "home_moneyline": home_ml,
        "away_moneyline": away_ml,
        "spread_home": spread_home,
        "spread_home_price": spread_home_price,
        "spread_away_price": spread_away_price,
        "total_line": total_line,
        "over_price": over_price,
        "under_price": under_price,
    }


def _event_lookup_key(home_team: str, away_team: str, game_date: str | date) -> str:
    if isinstance(game_date, date):
        gd = game_date.isoformat()
    else:
        gd = str(game_date)[:10]
    return f"{_normalize_team(home_team)}|{_normalize_team(away_team)}|{gd}"


def _load_cache() -> dict | None:
    if not LIVE_CACHE_PATH.exists():
        return None
    try:
        return json.loads(LIVE_CACHE_PATH.read_text())
    except json.JSONDecodeError:
        return None


def _save_cache(payload: dict) -> None:
    LIVE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    LIVE_CACHE_PATH.write_text(json.dumps(payload, indent=2))


def _cache_fresh(cache: dict, max_age_hours: int) -> bool:
    fetched = cache.get("fetched_at")
    if not fetched:
        return False
    try:
        ts = datetime.fromisoformat(fetched)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
    except ValueError:
        return False
    return datetime.now(timezone.utc) - ts < timedelta(hours=max_age_hours)


def fetch_live_odds(*, force: bool = False) -> dict:
    """Fetch NBA odds from The Odds API or return cached snapshot."""
    settings = get_settings()
    cache = _load_cache()

    if not force and cache and _cache_fresh(cache, settings.odds_cache_hours):
        return cache

    if not settings.odds_api_key:
        return {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "source": "none",
            "error": "ODDS_API_KEY not set — sign up at https://the-odds-api.com/",
            "requests_remaining": None,
            "events": cache.get("events", []) if cache else [],
            "stale": bool(cache),
        }

    params = {
        "apiKey": settings.odds_api_key,
        "regions": settings.odds_api_regions,
        "markets": "h2h,spreads,totals",
        "oddsFormat": "american",
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(ODDS_API_URL, params=params)
            response.raise_for_status()
            raw = response.json()
    except httpx.HTTPError as exc:
        stale_events = cache.get("events", []) if cache else []
        return {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "source": "the-odds-api",
            "error": str(exc),
            "requests_remaining": cache.get("requests_remaining") if cache else None,
            "events": stale_events,
            "stale": True,
        }

    events = [parsed for e in raw if (parsed := _parse_event(e))]
    remaining = response.headers.get("x-requests-remaining")
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "the-odds-api",
        "error": None,
        "requests_remaining": int(remaining) if remaining is not None else None,
        "events": events,
        "stale": False,
    }
    _save_cache(payload)
    return payload


def get_odds_status() -> dict:
    settings = get_settings()
    cache = _load_cache() or {}
    return {
        "configured": bool(settings.odds_api_key),
        "cache_path": str(LIVE_CACHE_PATH),
        "fetched_at": cache.get("fetched_at"),
        "requests_remaining": cache.get("requests_remaining"),
        "event_count": len(cache.get("events", [])),
        "stale": cache.get("stale", False),
        "error": cache.get("error"),
        "signup_url": "https://the-odds-api.com/",
        "budget_note": "Free tier: 500 requests/month — cache refreshes every "
        f"{settings.odds_cache_hours}h unless forced via make daily",
    }


def _build_event_index(events: list[dict]) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for event in events:
        key = _event_lookup_key(event["home_team"], event["away_team"], event["game_date"])
        index[key] = event
    return index


def enrich_predictions(predictions: list[dict], *, force_fetch: bool = False) -> list[dict]:
    """Attach live market lines, implied probabilities, and Kelly-style hints."""
    if not predictions:
        return predictions

    import sys

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    from ml.odds.betting import (
        american_to_implied_prob,
        pick_moneyline_side,
        pick_spread_side,
        pick_total_side,
        remove_vig,
    )

    snapshot = fetch_live_odds(force=force_fetch)
    index = _build_event_index(snapshot.get("events", []))
    odds_meta = {
        "odds_fetched_at": snapshot.get("fetched_at"),
        "odds_requests_remaining": snapshot.get("requests_remaining"),
        "odds_stale": snapshot.get("stale", False),
    }

    if not get_settings().odds_api_key:
        for pred in predictions:
            pred.update(odds_meta)
            pred["market_available"] = False
            pred["odds_hint"] = (
                "Sign up for a free Odds API key at the-odds-api.com and set ODDS_API_KEY in .env"
            )
        return predictions

    for pred in predictions:
        pred.update(odds_meta)
        home = pred.get("home_team") or ""
        away = pred.get("away_team") or ""
        game_date = pred.get("game_date") or ""
        event = index.get(_event_lookup_key(home, away, game_date))

        if not event:
            pred["market_available"] = False
            pred["odds_hint"] = "No live line matched for this game yet"
            continue

        pred["market_available"] = True
        pred["market_bookmaker"] = event.get("bookmaker")
        hints: list[str] = []

        model_home_prob = float(pred["home_win_prob"])
        predicted_margin = float(pred["predicted_home_score"]) - float(pred["predicted_away_score"])
        predicted_total = float(pred["predicted_total"])

        if event.get("home_moneyline") is not None and event.get("away_moneyline") is not None:
            ml = pick_moneyline_side(
                model_home_prob,
                int(event["home_moneyline"]),
                int(event["away_moneyline"]),
            )
            raw_home = american_to_implied_prob(int(event["home_moneyline"]))
            raw_away = american_to_implied_prob(int(event["away_moneyline"]))
            mkt_home, mkt_away = remove_vig(raw_home, raw_away)
            pred["market_home_moneyline"] = int(event["home_moneyline"])
            pred["market_away_moneyline"] = int(event["away_moneyline"])
            pred["market_home_implied_prob"] = round(mkt_home, 4)
            pred["market_away_implied_prob"] = round(mkt_away, 4)
            pred["ml_pick_side"] = ml["side"]
            pred["ml_edge"] = ml["edge"]
            pred["ml_quarter_kelly_pct"] = ml["quarter_kelly_pct"]
            side_label = home if ml["side"] == "home" else away
            hints.append(
                f"ML {side_label}: model {ml['model_prob']*100:.0f}% vs market "
                f"{ml['market_prob']*100:.0f}% · edge {ml['edge']*100:+.1f}% · "
                f"¼-Kelly {ml['quarter_kelly_pct']:.1f}%"
            )

        if (
            event.get("spread_home") is not None
            and event.get("spread_home_price") is not None
            and event.get("spread_away_price") is not None
        ):
            spread = pick_spread_side(
                predicted_margin,
                float(event["spread_home"]),
                int(event["spread_home_price"]),
                int(event["spread_away_price"]),
            )
            pred["market_spread_home"] = float(event["spread_home"])
            pred["market_spread_home_price"] = int(event["spread_home_price"])
            pred["spread_pick_side"] = spread["side"]
            pred["spread_cover_prob_model"] = spread["cover_prob"]
            pred["spread_cover_prob_market"] = spread["market_cover_prob"]
            pred["spread_edge"] = spread["edge"]
            pred["spread_quarter_kelly_pct"] = spread["quarter_kelly_pct"]
            side_label = home if spread["side"] == "home" else away
            line = spread["line"]
            line_str = f"{line:+.1f}" if spread["side"] == "home" else f"{line:+.1f}"
            hints.append(
                f"Spread {side_label} {line_str}: cover {spread['cover_prob']*100:.0f}% vs "
                f"market {spread['market_cover_prob']*100:.0f}% · edge "
                f"{spread['edge']*100:+.1f}% · ¼-Kelly {spread['quarter_kelly_pct']:.1f}%"
            )

        if (
            event.get("total_line") is not None
            and event.get("over_price") is not None
            and event.get("under_price") is not None
        ):
            total = pick_total_side(
                predicted_total,
                float(event["total_line"]),
                int(event["over_price"]),
                int(event["under_price"]),
            )
            pred["market_total"] = float(event["total_line"])
            pred["total_pick_side"] = total["side"]
            pred["total_win_prob_model"] = total["win_prob"]
            pred["total_win_prob_market"] = total["market_prob"]
            pred["total_edge"] = total["edge"]
            pred["total_quarter_kelly_pct"] = total["quarter_kelly_pct"]
            hints.append(
                f"Total {total['side'].title()} {total['line']}: model "
                f"{total['win_prob']*100:.0f}% vs market {total['market_prob']*100:.0f}% · "
                f"edge {total['edge']*100:+.1f}% · ¼-Kelly {total['quarter_kelly_pct']:.1f}%"
            )

        pred["odds_hint"] = " · ".join(hints) if hints else "Market data partial for this game"

    return predictions
