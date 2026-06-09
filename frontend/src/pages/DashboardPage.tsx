import { useQuery } from "@tanstack/react-query"

import { getGames, getHealth, getTeams, getUpcomingPredictions } from "@/api/client"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function DashboardPage() {
  const health = useQuery({ queryKey: ["health"], queryFn: getHealth })
  const teams = useQuery({ queryKey: ["teams"], queryFn: getTeams })
  const games = useQuery({ queryKey: ["games", { limit: 10 }], queryFn: () => getGames({ limit: 10 }) })
  const predictions = useQuery({ queryKey: ["predictions"], queryFn: getUpcomingPredictions })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">League Dashboard</h2>
        <p className="text-sm text-muted-foreground">
          Overview of teams, recent games, and model predictions.
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
            <CardDescription>Seasons configured</CardDescription>
            <CardTitle className="text-base font-medium">
              {health.data?.seasons_configured.join(", ") ?? "—"}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Upcoming predictions</CardTitle>
          <CardDescription>
            Placeholder until ML pipeline is trained. Shows moneyline, spread, and total targets.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {predictions.isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
          {predictions.data?.length === 0 && (
            <p className="text-sm text-muted-foreground">
              No scheduled games in DB yet. Run the ETL backfill after starting Postgres.
            </p>
          )}
          <div className="space-y-3">
            {predictions.data?.map((p) => (
              <div
                key={p.game_id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border/60 bg-card/50 px-4 py-3"
              >
                <div>
                  <p className="font-medium">Game {p.game_id}</p>
                  <p className="text-xs text-muted-foreground">{p.note}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary">
                    ML {(p.home_win_prob * 100).toFixed(0)}% home
                  </Badge>
                  <Badge variant="outline">Spread {p.predicted_spread > 0 ? "+" : ""}{p.predicted_spread}</Badge>
                  <Badge variant="outline">O/U {p.predicted_total.toFixed(1)}</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
