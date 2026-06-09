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
  home_win_prob: number
  predicted_home_score: number
  predicted_away_score: number
  predicted_spread: number
  predicted_total: number
  model_version: string
  note?: string
}

export interface Health {
  status: string
  seasons_configured: string[]
}
