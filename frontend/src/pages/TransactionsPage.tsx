import { useQuery } from "@tanstack/react-query"
import { useState } from "react"

import { getHealth, getTransactionTypes, getTransactions } from "@/api/client"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const TYPE_VARIANTS: Record<string, "default" | "secondary" | "outline"> = {
  trade: "default",
  signing: "secondary",
  waiver: "outline",
  claim: "outline",
  coaching: "secondary",
  retirement: "outline",
  draft: "secondary",
  other: "outline",
}

export function TransactionsPage() {
  const [season, setSeason] = useState("")
  const [type, setType] = useState("")

  const health = useQuery({ queryKey: ["health"], queryFn: getHealth })
  const types = useQuery({ queryKey: ["transaction-types"], queryFn: getTransactionTypes })
  const transactions = useQuery({
    queryKey: ["transactions", season, type],
    queryFn: () =>
      getTransactions({
        season: season || undefined,
        transaction_type: type || undefined,
        limit: 200,
      }),
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Transactions</h2>
        <p className="text-sm text-muted-foreground">
          League-wide trades, signings, and waivers from Basketball Reference.
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        <select
          value={season}
          onChange={(e) => setSeason(e.target.value)}
          className="h-9 rounded-lg border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-ring/50"
        >
          <option value="">All configured seasons</option>
          {health.data?.seasons_configured.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="h-9 rounded-lg border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-ring/50"
        >
          <option value="">All types</option>
          {types.data?.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Timeline</CardTitle>
          <CardDescription>
            {transactions.data?.length ?? 0} transactions
            {transactions.isLoading && " — loading…"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {transactions.data?.length === 0 && !transactions.isLoading && (
            <p className="text-sm text-muted-foreground">
              No transactions yet. Run <code className="text-xs">make phase2b</code> from the repo root.
            </p>
          )}
          <div className="space-y-3">
            {transactions.data?.map((tx) => (
              <div
                key={tx.id}
                className="rounded-lg border border-border/60 bg-card/50 px-4 py-3"
              >
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <span className="text-sm font-medium">{tx.transaction_date}</span>
                  <Badge variant={TYPE_VARIANTS[tx.transaction_type] ?? "outline"}>
                    {tx.transaction_type}
                  </Badge>
                  <span className="text-xs text-muted-foreground">{tx.season}</span>
                </div>
                <p className="text-sm leading-relaxed text-foreground/90">{tx.description}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
