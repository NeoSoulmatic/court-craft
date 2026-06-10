"""Unit tests for betting math helpers."""

from ml.odds.betting import (
    american_to_decimal,
    american_to_implied_prob,
    kelly_fraction,
    pick_moneyline_side,
    pick_spread_side,
    remove_vig,
    spread_cover_prob_home,
    total_over_prob,
)


def test_american_to_decimal_favorites_and_dogs() -> None:
    assert american_to_decimal(-110) == 1 + 100 / 110
    assert american_to_decimal(150) == 2.5


def test_american_to_implied_prob() -> None:
    assert abs(american_to_implied_prob(-110) - 0.5238) < 0.001
    assert abs(american_to_implied_prob(100) - 0.5) < 0.001


def test_remove_vig_normalizes_to_one() -> None:
    home, away = remove_vig(0.55, 0.55)
    assert abs(home + away - 1.0) < 1e-9
    assert home == away == 0.5


def test_kelly_zero_when_no_edge() -> None:
    assert kelly_fraction(0.5238, -110) == 0.0


def test_kelly_positive_with_edge() -> None:
    assert kelly_fraction(0.60, -110) > 0.0


def test_spread_cover_prob_favored_home() -> None:
    prob = spread_cover_prob_home(6.0, -4.5)
    assert prob > 0.54


def test_total_over_prob_above_line() -> None:
    assert total_over_prob(230.0, 220.5) > 0.5


def test_pick_moneyline_prefers_home_edge() -> None:
    pick = pick_moneyline_side(0.62, -120, 100)
    assert pick["side"] == "home"
    assert pick["edge"] > 0


def test_pick_spread_returns_quarter_kelly() -> None:
    pick = pick_spread_side(5.0, -3.5, -110, -110)
    assert pick["side"] in ("home", "away")
    assert pick["quarter_kelly_pct"] >= 0
