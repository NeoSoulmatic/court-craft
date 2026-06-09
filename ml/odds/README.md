# Historical odds (Phase 3)

## Selected source

**[kyleskom/NBA-Machine-Learning-Sports-Betting](https://github.com/kyleskom/NBA-Machine-Learning-Sports-Betting) `OddsData.sqlite`**

- Free, direct download from GitHub (no Kaggle account)
- SBR-style closing **spread** and **over/under** lines
- Covers our seasons via tables: `odds_2022-23`, `2023-24`, `2024-25`, `odds_2025-26`

Downloaded automatically by `make phase3` into `data/odds/OddsData.sqlite` (gitignored).

## Alternatives considered

| Dataset | Pros | Cons |
|---------|------|------|
| Kaggle `cviaxmiwnptr/nba-betting-data` | Clean CSV, closing lines through Jun 2025 | Requires Kaggle API; manual setup |
| Basketball Betting SQLite (visualize25) | Rich schema | Stops ~2020-21 |
| The Odds API | Live + historical (paid tier) | Not free at scale |

## Coverage caveat

The free `OddsData.sqlite` file has **partial 2025-26** lines (~514 of 1,230 games at time of ingest). Spread/total backtest metrics use only games with joined odds. Moneyline backtest uses all holdout games.

## v2

- Playoff odds (regular season only in v1)
- Optional Kaggle dataset merge for fuller 2025-26 coverage
- Paid Odds API for live line comparison (Phase 4)
