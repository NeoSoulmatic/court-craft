"""Betting math: implied probability, edge, and Kelly sizing."""

from __future__ import annotations

import math

# Backtest MAE ~12 pts margin; use slightly wider for cover probability
MARGIN_SIGMA = 12.0
TOTAL_SIGMA = 14.0
QUARTER_KELLY = 0.25


def american_to_decimal(american: int) -> float:
    if american == 0:
        raise ValueError("American odds cannot be zero")
    if american > 0:
        return 1.0 + american / 100.0
    return 1.0 + 100.0 / abs(american)


def american_to_implied_prob(american: int) -> float:
    if american > 0:
        return 100.0 / (american + 100.0)
    return abs(american) / (abs(american) + 100.0)


def remove_vig(*probs: float) -> list[float]:
    total = sum(probs)
    if total <= 0:
        return [0.0 for _ in probs]
    return [p / total for p in probs]


def kelly_fraction(win_prob: float, american: int) -> float:
    """Full Kelly fraction of bankroll for a single bet at given American odds."""
    if win_prob <= 0 or win_prob >= 1:
        return 0.0
    b = american_to_decimal(american) - 1.0
    q = 1.0 - win_prob
    edge = b * win_prob - q
    if edge <= 0 or b <= 0:
        return 0.0
    return edge / b


def _norm_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def spread_cover_prob_home(
    predicted_margin: float,
    spread_home: float,
    sigma: float = MARGIN_SIGMA,
) -> float:
    """P(home covers) where spread_home is the home line (negative = home favored)."""
    if sigma <= 0:
        return 0.5
    z = (predicted_margin + spread_home) / sigma
    return _norm_cdf(z)


def total_over_prob(
    predicted_total: float,
    total_line: float,
    sigma: float = TOTAL_SIGMA,
) -> float:
    if sigma <= 0:
        return 0.5
    z = (predicted_total - total_line) / sigma
    return _norm_cdf(z)


def quarter_kelly_pct(win_prob: float, american: int) -> float:
    return round(kelly_fraction(win_prob, american) * QUARTER_KELLY * 100.0, 2)


def ml_edge_pct(model_prob: float, market_prob: float) -> float:
    return round((model_prob - market_prob) * 100.0, 1)


def pick_spread_side(
    predicted_margin: float,
    spread_home: float,
    home_price: int,
    away_price: int,
) -> dict:
    """Recommend spread side with cover prob, edge vs market, and quarter-Kelly."""
    home_cover = spread_cover_prob_home(predicted_margin, spread_home)
    away_cover = 1.0 - home_cover
    market_home = american_to_implied_prob(home_price)
    market_away = american_to_implied_prob(away_price)
    home_edge = home_cover - market_home
    away_edge = away_cover - market_away

    if home_edge >= away_edge:
        side = "home"
        cover_prob = home_cover
        market_prob = market_home
        price = home_price
        line = spread_home
    else:
        side = "away"
        cover_prob = away_cover
        market_prob = market_away
        price = away_price
        line = -spread_home

    return {
        "side": side,
        "cover_prob": round(cover_prob, 4),
        "market_cover_prob": round(market_prob, 4),
        "edge": round(home_edge if side == "home" else away_edge, 4),
        "quarter_kelly_pct": quarter_kelly_pct(cover_prob, price),
        "line": line,
        "price": price,
    }


def pick_total_side(
    predicted_total: float,
    total_line: float,
    over_price: int,
    under_price: int,
) -> dict:
    over_prob = total_over_prob(predicted_total, total_line)
    under_prob = 1.0 - over_prob
    market_over = american_to_implied_prob(over_price)
    market_under = american_to_implied_prob(under_price)
    over_edge = over_prob - market_over
    under_edge = under_prob - market_under

    if over_edge >= under_edge:
        side = "over"
        win_prob = over_prob
        market_prob = market_over
        price = over_price
        edge = over_edge
    else:
        side = "under"
        win_prob = under_prob
        market_prob = market_under
        price = under_price
        edge = under_edge

    return {
        "side": side,
        "win_prob": round(win_prob, 4),
        "market_prob": round(market_prob, 4),
        "edge": round(edge, 4),
        "quarter_kelly_pct": quarter_kelly_pct(win_prob, price),
        "line": total_line,
        "price": price,
    }


def pick_moneyline_side(
    model_home_prob: float,
    home_price: int,
    away_price: int,
) -> dict:
    model_away_prob = 1.0 - model_home_prob
    raw_home = american_to_implied_prob(home_price)
    raw_away = american_to_implied_prob(away_price)
    market_home, market_away = remove_vig(raw_home, raw_away)
    home_edge = model_home_prob - market_home
    away_edge = model_away_prob - market_away

    if home_edge >= away_edge:
        side = "home"
        model_prob = model_home_prob
        market_prob = market_home
        price = home_price
        edge = home_edge
    else:
        side = "away"
        model_prob = model_away_prob
        market_prob = market_away
        price = away_price
        edge = away_edge

    return {
        "side": side,
        "model_prob": round(model_prob, 4),
        "market_prob": round(market_prob, 4),
        "edge": round(edge, 4),
        "quarter_kelly_pct": quarter_kelly_pct(model_prob, price),
        "price": price,
    }
