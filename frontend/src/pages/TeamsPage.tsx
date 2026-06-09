import { useQuery } from "@tanstack/react-query"

import { getTeams } from "@/api/client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export function TeamsPage() {
  const teams = useQuery({ queryKey: ["teams"], queryFn: getTeams })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Teams</h2>
        <p className="text-sm text-muted-foreground">All 30 NBA teams.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>League teams</CardTitle>
          <CardDescription>{teams.data?.length ?? 0} teams</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Abbr</TableHead>
                <TableHead>Team</TableHead>
                <TableHead>Conference</TableHead>
                <TableHead>Division</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {teams.data?.map((team) => (
                <TableRow key={team.id}>
                  <TableCell className="font-mono">{team.abbreviation}</TableCell>
                  <TableCell>{team.full_name}</TableCell>
                  <TableCell>{team.conference ?? "—"}</TableCell>
                  <TableCell>{team.division ?? "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
