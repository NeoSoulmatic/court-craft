import { BarChart3, LayoutDashboard, Trophy, Users, UserCircle, FileText, Brain } from "lucide-react"
import { NavLink, Outlet } from "react-router-dom"

import { cn } from "@/lib/utils"
import { Separator } from "@/components/ui/separator"

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/games", label: "Games", icon: Trophy },
  { to: "/teams", label: "Teams", icon: Users },
  { to: "/players", label: "Players", icon: UserCircle },
  { to: "/draft", label: "Draft", icon: FileText },
  { to: "/model", label: "Model", icon: Brain },
]

export function AppShell() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border/60 bg-card/40 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-xl bg-primary/15 text-primary">
              <BarChart3 className="size-5" />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">Court Craft</h1>
              <p className="text-xs text-muted-foreground">NBA analytics & predictions</p>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6">
        <aside className="hidden w-56 shrink-0 md:block">
          <nav className="sticky top-6 space-y-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                    isActive
                      ? "bg-primary/15 text-primary"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  )
                }
              >
                <Icon className="size-4" />
                {label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="min-w-0 flex-1">
          <Outlet />
        </main>
      </div>

      <footer className="mt-8 border-t border-border/60">
        <div className="mx-auto max-w-7xl px-4 py-4 text-center text-xs text-muted-foreground">
          <Separator className="mb-4" />
          Predictions are for education and portfolio demonstration only. Not betting advice.
        </div>
      </footer>
    </div>
  )
}
