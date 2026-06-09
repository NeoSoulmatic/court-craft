import { useQuery } from "@tanstack/react-query"

import { api } from "@/api/client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface MarketMetric {
  games?: number
  games_with_odds?: number
  accuracy?: number
  hit_rate?: number
  model_pick_hit_rate?: number
  model_over_hit_rate?: number
  vegas_baseline_over_50?: number
  vegas_over_rate?: number
  note?: string
}

interface Backtest {
  model_version: string
  train_seasons: string[]
  test_season: string
  regular_season_only: boolean
  moneyline: MarketMetric
  spread: MarketMetric
  total: MarketMetric
  errors: { margin_mae: number; total_mae: number }
  odds_source: string
  odds_coverage_note: string
}

function pct(value: number | undefined | null) {
  if (value == null) return "—"
  return `${(value * 100).toFixed(1)}%`
}

export function ModelPage() {
  const backtest = useQuery({
    queryKey: ["model-backtest"],
    queryFn: async () => {
      const { data } = await api.get<Backtest>("/model/backtest")
      return data
    },
    retry: false,
  })

  if (backtest.isError) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Model performance</h2>
          <p className="text-sm text-muted-foreground">
            Run <code className="text-xs">make phase3</code> to train models and generate backtest
            metrics.
          </p>
        </div>
      </div>
    )
  }

  const data = backtest.data

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Model performance</h2>
        <p className="text-sm text-muted-foreground">
          {data
            ? `Holdout: ${data.test_season} · Trained on ${data.train_seasons.join(", ")} · ${data.model_version}`
            : "Loading backtest results…"}
        </p>
      </div>

      {data && (
        <>
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Margin MAE</CardDescription>
                <CardTitle className="text-3xl">{data.errors.margin_mae}</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total MAE</CardDescription>
                <CardTitle className="text-3xl">{data.errors.total_mae}</CardTitle>
              </CardHeader>
            </Card>
          </div>

          <Tabs defaultValue="moneyline">
            <TabsList>
              <TabsTrigger value="moneyline">Moneyline</TabsTrigger>
              <TabsTrigger value="spread">Spread</TabsTrigger>
              <TabsTrigger value="total">Total</TabsTrigger>
            </TabsList>
            <TabsContent value="moneyline">
              <MetricCard
                title="Moneyline accuracy"
                description={`${data.moneyline.games ?? 0} games · ${data.test_season} holdout`}
                value={pct(data.moneyline.accuracy)}
              />
            </TabsContent>
            <TabsContent value="spread">
              <MetricCard
                title="Spread — model pick hit rate"
                description={`${data.spread.games_with_odds ?? 0} games with closing lines`}
                value={pct(data.spread.model_pick_hit_rate)}
                extra={`Vegas baseline: ${pct(data.spread.vegas_baseline_over_50)}`}
              />
            </TabsContent>
            <TabsContent value="total">
              <MetricCard
                title="Over/under — model over hit rate"
                description={`${data.total.games_with_odds ?? 0} games with closing totals`}
                value={pct(data.total.model_over_hit_rate)}
                extra={`Actual over rate: ${pct(data.total.vegas_over_rate)}`}
              />
            </TabsContent>
          </Tabs>

          <Card>
            <CardHeader>
              <CardTitle>Data notes</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              <p>{data.odds_coverage_note}</p>
              <p>Odds source: {data.odds_source}</p>
              <p>Regular season only for v1. Playoffs planned for v2.</p>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

function MetricCard({
  title,
  description,
  value,
  extra,
}: {
  title: string
  description: string
  value: string
  extra?: string
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-4xl font-semibold tracking-tight">{value}</p>
        {extra && <p className="mt-2 text-sm text-muted-foreground">{extra}</p>}
      </CardContent>
    </Card>
  )
}
