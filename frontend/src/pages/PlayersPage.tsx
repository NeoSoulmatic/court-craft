import { useQuery } from "@tanstack/react-query"

import { getPlayers } from "@/api/client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export function PlayersPage() {
  const players = useQuery({
    queryKey: ["players"],
    queryFn: () => getPlayers({ limit: 200 }),
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Players</h2>
        <p className="text-sm text-muted-foreground">
          Active players (populated after player ETL in Phase 2).
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Roster</CardTitle>
          <CardDescription>{players.data?.length ?? 0} players</CardDescription>
        </CardHeader>
        <CardContent>
          {players.data?.length === 0 && !players.isLoading && (
            <p className="text-sm text-muted-foreground">
              No players yet. Player ingest ships in Phase 2.
            </p>
          )}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Position</TableHead>
                <TableHead>Team ID</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {players.data?.map((player) => (
                <TableRow key={player.id}>
                  <TableCell>{player.full_name}</TableCell>
                  <TableCell>{player.position ?? "—"}</TableCell>
                  <TableCell>{player.team_id ?? "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
