import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export function ModelPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Model performance</h2>
        <p className="text-sm text-muted-foreground">
          Backtest results vs closing lines — ships in Phase 3.
        </p>
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
            description="Target: 62–65% on held-out season"
            placeholder="Run ml/backtest.py after training"
          />
        </TabsContent>
        <TabsContent value="spread">
          <MetricCard
            title="Spread cover rate"
            description="Target: 51–53% vs closing line"
            placeholder="Requires historical odds CSV"
          />
        </TabsContent>
        <TabsContent value="total">
          <MetricCard
            title="Over/under hit rate"
            description="Target: 51–53% vs closing total"
            placeholder="Requires historical odds CSV"
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}

function MetricCard({
  title,
  description,
  placeholder,
}: {
  title: string
  description: string
  placeholder: string
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{placeholder}</p>
      </CardContent>
    </Card>
  )
}
