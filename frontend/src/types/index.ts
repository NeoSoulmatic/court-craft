export interface Team {
  id: number
  abbreviation: string
  full_name: string
  city: string
  nickname: string
  conference: string | null
  division: string | null
}

export interface Player {
  id: number
  full_name: string
  team_id: number | null
  team_abbreviation: string | null
  position: string | null
  height: string | null
  weight: number | null
  is_active: boolean
}

export interface Game {
  id: string
  season: string
  game_date: string
  game_datetime_utc: string | null
  home_team_id: number
  away_team_id: number
  home_score: number | null
  away_score: number | null
  status: string
  home_team?: Team
  away_team?: Team
}

export interface DraftPick {
  id: number
  season: string
  round: number
  pick_overall: number
  team_id: number | null
  player_id: number | null
  player_name: string
  college: string | null
}

export interface Prediction {
  game_id: string
  game_date?: string | null
  season_type?: string
  home_team?: string | null
  away_team?: string | null
  home_win_prob: number
  predicted_home_score: number
  predicted_away_score: number
  predicted_spread: number
  predicted_total: number
  model_version: string
  note?: string
  market_available?: boolean
  market_bookmaker?: string | null
  market_home_moneyline?: number | null
  market_away_moneyline?: number | null
  market_home_implied_prob?: number | null
  market_spread_home?: number | null
  market_total?: number | null
  ml_pick_side?: string | null
  ml_edge?: number | null
  ml_quarter_kelly_pct?: number | null
  spread_pick_side?: string | null
  spread_cover_prob_model?: number | null
  spread_cover_prob_market?: number | null
  spread_edge?: number | null
  spread_quarter_kelly_pct?: number | null
  total_pick_side?: string | null
  total_win_prob_model?: number | null
  total_win_prob_market?: number | null
  total_edge?: number | null
  total_quarter_kelly_pct?: number | null
  odds_fetched_at?: string | null
  odds_requests_remaining?: number | null
  odds_stale?: boolean
  odds_hint?: string | null
}

export interface OddsStatus {
  configured: boolean
  cache_path: string
  fetched_at?: string | null
  requests_remaining?: number | null
  event_count: number
  stale: boolean
  error?: string | null
  signup_url: string
  budget_note: string
}

export interface Transaction {
  id: number
  transaction_date: string
  season: string
  transaction_type: string
  description: string
  source: string
}

export interface Health {
  status: string
  seasons_configured: string[]
}
