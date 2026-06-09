import { useQuery } from "@tanstack/react-query"
import { useState } from "react"

import { getDraftPicks, getDraftSeasons } from "@/api/client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export function DraftPage() {
  const [season, setSeason] = useState("")

  const seasons = useQuery({ queryKey: ["draft-seasons"], queryFn: getDraftSeasons })
  const picks = useQuery({
    queryKey: ["draft", season],
    queryFn: () => getDraftPicks({ season: season || undefined, limit: 120 }),
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Draft</h2>
        <p className="text-sm text-muted-foreground">
          Historical draft picks from NBA draft history.
        </p>
      </div>

      <select
        value={season}
        onChange={(e) => setSeason(e.target.value)}
        className="h-9 rounded-lg border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-ring/50"
      >
        <option value="">Latest picks</option>
        {seasons.data?.map((y) => (
          <option key={y} value={y}>
            {y} draft
          </option>
        ))}
      </select>

      <Card>
        <CardHeader>
          <CardTitle>Draft picks</CardTitle>
          <CardDescription>
            {season ? `${season} draft` : "Most recent"} — {picks.data?.length ?? 0} picks
          </CardDescription>
        </CardHeader>
        <CardContent>
          {picks.data?.length === 0 && !picks.isLoading && (
            <p className="text-sm text-muted-foreground">
              No draft data yet. Run <code className="text-xs">make phase2</code> from the repo root.
            </p>
          )}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Year</TableHead>
                <TableHead>Pick</TableHead>
                <TableHead>Rd</TableHead>
                <TableHead>Player</TableHead>
                <TableHead>College</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {picks.data?.map((pick) => (
                <TableRow key={pick.id}>
                  <TableCell>{pick.season}</TableCell>
                  <TableCell>#{pick.pick_overall}</TableCell>
                  <TableCell>{pick.round}</TableCell>
                  <TableCell className="font-medium">{pick.player_name}</TableCell>
                  <TableCell>{pick.college ?? "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
