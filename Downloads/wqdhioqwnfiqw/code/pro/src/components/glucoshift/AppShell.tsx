import { Link, useRouterState } from "@tanstack/react-router";
import { Activity, HeartPulse, Home, LogOut, MessageCircleHeart, Users } from "lucide-react";
import { type ReactNode } from "react";

import { AuthScreen } from "./AuthScreen";
import { CoachDrawer } from "./CoachDrawer";
import { PairDialog } from "./PairDialog";
import { Badge } from "@/components/ui/badge";
import { useGlucoShift } from "@/lib/glucoshift-store";
import { cn } from "@/lib/utils";

const NAV = [
  { to: "/", label: "Hoy", icon: Home },
  { to: "/salud", label: "Mi salud", icon: HeartPulse },
  { to: "/familia", label: "Familia", icon: Users },
] as const;

export function AppShell({ children }: { children: ReactNode }) {
  const { loading, session, mode, points, profile, setChatOpen, signOut } = useGlucoShift();
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const large = mode === "paciente";

  const frame = (content: ReactNode) => (
    <div className="min-h-screen bg-slate-100/60">
      <div
        className={cn(
          "mx-auto flex min-h-screen max-w-md flex-col border-x border-slate-200 bg-slate-50 shadow-xl",
          large && "text-[1.02rem]",
        )}
      >
        {content}
      </div>
    </div>
  );

  if (loading) {
    return frame(
      <div className="flex flex-1 items-center justify-center text-sm text-muted-foreground">
        Cargando GlucoShift...
      </div>,
    );
  }

  if (!session) return frame(<AuthScreen />);

  return frame(
    <>
      <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-slate-50/95 backdrop-blur">
        <div className="flex items-center gap-2 px-4 pt-4 pb-3">
          <div className="flex size-9 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
            <Activity className="size-5" />
          </div>
          <div className="mr-auto leading-tight">
            <p className="font-display text-lg font-semibold text-foreground">GlucoShift</p>
            <p className="text-[11px] text-muted-foreground">
              {profile?.full_name || "Curva plana, en familia"}
            </p>
          </div>
          <Badge
            variant="outline"
            className="rounded-full border-primary/30 bg-success-soft text-[11px] text-accent-foreground"
          >
            {mode === "paciente" ? "Paciente" : "Acompañante"}
          </Badge>
          <PairDialog />
        </div>
        <div className="flex items-center gap-2 px-4 pb-3">
          <button
            type="button"
            onClick={() => void signOut()}
            className="flex items-center gap-1.5 rounded-full bg-slate-200/70 px-3 py-1.5 text-xs font-semibold text-muted-foreground"
          >
            <LogOut className="size-3.5" /> Salir
          </button>
          <span className="ml-auto rounded-full bg-warning-soft px-3 py-1 text-xs font-semibold text-warning-foreground">
            {points} pts
          </span>
        </div>
      </header>

      <main className="flex-1 px-4 pt-4 pb-28">{children}</main>

      <button
        type="button"
        onClick={() => setChatOpen(true)}
        className="fixed bottom-24 left-1/2 z-40 ml-[7.5rem] flex size-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg shadow-primary/30 transition-transform active:scale-95"
        aria-label="Abrir Coach Gluco"
      >
        <MessageCircleHeart className="size-6" />
      </button>

      <nav className="fixed bottom-0 z-30 w-full max-w-md border-t border-slate-200 bg-white/95 backdrop-blur">
        <ul className="flex items-stretch">
          {NAV.map((item) => {
            const active = pathname === item.to;
            const Icon = item.icon;
            return (
              <li key={item.to} className="flex-1">
                <Link
                  to={item.to}
                  className={cn(
                    "flex flex-col items-center gap-1 py-3 text-[11px] font-medium transition-colors",
                    active ? "text-primary" : "text-muted-foreground",
                  )}
                >
                  <Icon className={cn("size-5", active && "scale-110")} />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <CoachDrawer />
    </>,
  );
}
