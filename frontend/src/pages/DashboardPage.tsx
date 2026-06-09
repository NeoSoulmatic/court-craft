import { useQuery } from "@tanstack/react-query"

import { getGames, getOddsStatus, getTeams, getUpcomingPredictions } from "@/api/client"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { Prediction } from "@/types"

function formatPct(value: number | null | undefined) {
  if (value == null) return "—"
  return `${(value * 100).toFixed(0)}%`
}

function EdgeBadge({ edge, label }: { edge: number | null | undefined; label: string }) {
  if (edge == null) return null
  const pct = edge * 100
  const variant = pct > 0 ? "default" : "secondary"
  return (
    <Badge variant={variant} className="text-xs">
      {label} {pct > 0 ? "+" : ""}
      {pct.toFixed(1)}%
    </Badge>
  )
}

function PredictionCard({ p }: { p: Prediction }) {
  const hasMarket = p.market_available

  return (
    <div className="rounded-lg border border-border/60 bg-card/50 px-4 py-3 space-y-3">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="font-medium">
            {p.away_team && p.home_team
              ? `${p.away_team} @ ${p.home_team}`
              : `Game ${p.game_id}`}
          </p>
          <p className="text-xs text-muted-foreground">
            {p.game_date}
            {p.season_type === "Playoffs" && (
              <Badge variant="default" className="ml-2">
                Playoffs
              </Badge>
            )}
            {p.market_bookmaker && (
              <span className="ml-2 capitalize">via {p.market_bookmaker}</span>
            )}
          </p>
          {p.note && <p className="text-xs text-amber-400/90 mt-1">{p.note}</p>}
        </div>
        <div className="flex flex-wrap gap-2 justify-end">
          <Badge variant="secondary">Model ML {formatPct(p.home_win_prob)} home</Badge>
          <Badge variant="outline">
            Spread {p.predicted_spread > 0 ? "+" : ""}
            {p.predicted_spread}
          </Badge>
          <Badge variant="outline">O/U {p.predicted_total.toFixed(1)}</Badge>
        </div>
      </div>

      {hasMarket ? (
        <div className="grid gap-3 md:grid-cols-3 text-sm border-t border-border/40 pt-3">
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Moneyline
            </p>
            <p>
              Market {formatPct(p.market_home_implied_prob)} home
              {p.market_home_moneyline != null && (
                <span className="text-muted-foreground text-xs ml-1">
                  ({p.market_home_moneyline > 0 ? "+" : ""}
                  {p.market_home_moneyline})
                </span>
              )}
            </p>
            <div className="flex flex-wrap gap-1">
              <EdgeBadge edge={p.ml_edge} label="Edge" />
              {p.ml_quarter_kelly_pct != null && p.ml_quarter_kelly_pct > 0 && (
                <Badge variant="outline" className="text-xs">
                  ¼-Kelly {p.ml_quarter_kelly_pct.toFixed(1)}%
                </Badge>
              )}
            </div>
          </div>
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Spread
            </p>
            <p>
              Line {p.market_spread_home != null ? p.market_spread_home.toFixed(1) : "—"}
              <span className="text-muted-foreground text-xs ml-2">
                Model cover {formatPct(p.spread_cover_prob_model)}
              </span>
            </p>
            <div className="flex flex-wrap gap-1">
              <EdgeBadge edge={p.spread_edge} label="Edge" />
              {p.spread_quarter_kelly_pct != null && p.spread_quarter_kelly_pct > 0 && (
                <Badge variant="outline" className="text-xs">
                  ¼-Kelly {p.spread_quarter_kelly_pct.toFixed(1)}%
                </Badge>
              )}
            </div>
          </div>
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Total
            </p>
            <p>
              Line {p.market_total?.toFixed(1) ?? "—"}
              <span className="text-muted-foreground text-xs ml-2">
                Model {p.total_pick_side ?? "—"} {formatPct(p.total_win_prob_model)}
              </span>
            </p>
            <div className="flex flex-wrap gap-1">
              <EdgeBadge edge={p.total_edge} label="Edge" />
              {p.total_quarter_kelly_pct != null && p.total_quarter_kelly_pct > 0 && (
                <Badge variant="outline" className="text-xs">
                  ¼-Kelly {p.total_quarter_kelly_pct.toFixed(1)}%
                </Badge>
              )}
            </div>
          </div>
        </div>
      ) : (
        <p className="text-xs text-muted-foreground border-t border-border/40 pt-2">
          {p.odds_hint ?? "Live market lines unavailable"}
        </p>
      )}

      {p.odds_hint && hasMarket && (
        <p className="text-xs text-muted-foreground/90 leading-relaxed">{p.odds_hint}</p>
      )}
    </div>
  )
}

export function DashboardPage() {
  const teams = useQuery({ queryKey: ["teams"], queryFn: getTeams })
  const games = useQuery({ queryKey: ["games", { limit: 10 }], queryFn: () => getGames({ limit: 10 }) })
  const predictions = useQuery({ queryKey: ["predictions"], queryFn: getUpcomingPredictions })
  const oddsStatus = useQuery({ queryKey: ["odds-status"], queryFn: getOddsStatus })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">League Dashboard</h2>
        <p className="text-sm text-muted-foreground">
          Model vs market — implied win rates and quarter-Kelly sizing hints.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Teams loaded</CardDescription>
            <CardTitle className="text-3xl">{teams.data?.length ?? "—"}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Recent games</CardDescription>
            <CardTitle className="text-3xl">{games.data?.length ?? "—"}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Live odds</CardDescription>
            <CardTitle className="text-base font-medium">
              {oddsStatus.data?.configured
                ? `${oddsStatus.data.event_count} events`
                : "Not configured"}
            </CardTitle>
            {oddsStatus.data && (
              <p className="text-xs text-muted-foreground">
                {oddsStatus.data.configured
                  ? oddsStatus.data.budget_note
                  : `Get a free key at ${oddsStatus.data.signup_url}`}
              </p>
            )}
          </CardHeader>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Upcoming predictions</CardTitle>
          <CardDescription>
            Model projections vs live market lines. Run <code className="text-xs">make daily</code>{" "}
            to refresh games, odds, and predictions.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {predictions.isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
          {predictions.data?.length === 0 && (
            <p className="text-sm text-muted-foreground">
              No predictions yet — need scheduled games and a trained model (make phase3).
            </p>
          )}
          <div className="space-y-3">
            {predictions.data?.map((p) => (
              <PredictionCard key={p.game_id} p={p} />
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-4">
            Education only — not betting advice. Kelly hints use quarter-Kelly at posted juice.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
