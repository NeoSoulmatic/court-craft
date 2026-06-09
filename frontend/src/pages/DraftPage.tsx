import { useQuery } from "@tanstack/react-query"

import { getDraftPicks } from "@/api/client"
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
  const picks = useQuery({
    queryKey: ["draft"],
    queryFn: () => getDraftPicks({ limit: 120 }),
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Draft</h2>
        <p className="text-sm text-muted-foreground">
          Draft pick explorer (CSV ingest in Phase 2).
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Draft picks</CardTitle>
          <CardDescription>{picks.data?.length ?? 0} picks</CardDescription>
        </CardHeader>
        <CardContent>
          {picks.data?.length === 0 && !picks.isLoading && (
            <p className="text-sm text-muted-foreground">
              No draft data yet. We will ingest from Kaggle / Basketball Reference in Phase 2.
            </p>
          )}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Year</TableHead>
                <TableHead>Pick</TableHead>
                <TableHead>Player</TableHead>
                <TableHead>College</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {picks.data?.map((pick) => (
                <TableRow key={pick.id}>
                  <TableCell>{pick.season}</TableCell>
                  <TableCell>#{pick.pick_overall}</TableCell>
                  <TableCell>{pick.player_name}</TableCell>
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
