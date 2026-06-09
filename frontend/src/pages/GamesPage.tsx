import { useQuery } from "@tanstack/react-query"

import { getGames } from "@/api/client"
import { StatusBadge } from "@/components/StatusBadge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export function GamesPage() {
  const games = useQuery({
    queryKey: ["games", { limit: 100 }],
    queryFn: () => getGames({ limit: 100 }),
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Games</h2>
        <p className="text-sm text-muted-foreground">Recent and scheduled games from the database.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Game log</CardTitle>
          <CardDescription>
            {games.isLoading ? "Loading…" : `${games.data?.length ?? 0} games`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Matchup</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Season</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {games.data?.map((game) => (
                <TableRow key={game.id}>
                  <TableCell>{game.game_date}</TableCell>
                  <TableCell>
                    {game.away_team?.abbreviation ?? game.away_team_id} @{" "}
                    {game.home_team?.abbreviation ?? game.home_team_id}
                  </TableCell>
                  <TableCell>
                    {game.home_score != null && game.away_score != null
                      ? `${game.away_score} – ${game.home_score}`
                      : "—"}
                  </TableCell>
                  <TableCell>{game.season}</TableCell>
                  <TableCell>
                    <StatusBadge status={game.status} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
