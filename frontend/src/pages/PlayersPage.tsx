import { useQuery } from "@tanstack/react-query"
import { useState } from "react"

import { getPlayers, getTeams } from "@/api/client"
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
  const [teamFilter, setTeamFilter] = useState<string>("")
  const [search, setSearch] = useState("")

  const teams = useQuery({ queryKey: ["teams"], queryFn: getTeams })
  const players = useQuery({
    queryKey: ["players", teamFilter, search],
    queryFn: () =>
      getPlayers({
        team_id: teamFilter ? Number(teamFilter) : undefined,
        search: search || undefined,
        limit: 300,
      }),
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Players</h2>
        <p className="text-sm text-muted-foreground">
          Active NBA rosters with position and team assignment.
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        <input
          type="search"
          placeholder="Search by name…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="h-9 rounded-lg border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-ring/50"
        />
        <select
          value={teamFilter}
          onChange={(e) => setTeamFilter(e.target.value)}
          className="h-9 rounded-lg border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-ring/50"
        >
          <option value="">All teams</option>
          {teams.data?.map((team) => (
            <option key={team.id} value={team.id}>
              {team.abbreviation} — {team.full_name}
            </option>
          ))}
        </select>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Roster</CardTitle>
          <CardDescription>{players.data?.length ?? 0} players</CardDescription>
        </CardHeader>
        <CardContent>
          {players.data?.length === 0 && !players.isLoading && (
            <p className="text-sm text-muted-foreground">
              No players yet. Run <code className="text-xs">make phase2</code> from the repo root.
            </p>
          )}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Team</TableHead>
                <TableHead>Pos</TableHead>
                <TableHead>Height</TableHead>
                <TableHead>Weight</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {players.data?.map((player) => (
                <TableRow key={player.id}>
                  <TableCell className="font-medium">{player.full_name}</TableCell>
                  <TableCell>{player.team_abbreviation ?? "—"}</TableCell>
                  <TableCell>{player.position ?? "—"}</TableCell>
                  <TableCell>{player.height ?? "—"}</TableCell>
                  <TableCell>{player.weight ? `${player.weight} lbs` : "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
