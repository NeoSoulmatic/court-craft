import { Badge } from "@/components/ui/badge"

export function StatusBadge({ status }: { status: string }) {
  const variant =
    status === "final" ? "default" : status === "scheduled" ? "secondary" : "outline"
  return <Badge variant={variant}>{status}</Badge>
}
