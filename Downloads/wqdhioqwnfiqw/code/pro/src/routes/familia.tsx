import { createFileRoute } from "@tanstack/react-router";
import { Heart, Users } from "lucide-react";

import { CaregiverDashboard } from "@/components/glucoshift/CaregiverDashboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useGlucoShift } from "@/lib/glucoshift-store";

export const Route = createFileRoute("/familia")({
  head: () => ({
    meta: [
      { title: "Familia — Panel del acompañante | GlucoShift" },
      {
        name: "description",
        content:
          "Sigue en vivo la adherencia de tu familiar desde tu propio teléfono, revisa su línea de tiempo y envíale recordatorios cariñosos.",
      },
      { property: "og:title", content: "Familia — Panel del acompañante | GlucoShift" },
      {
        property: "og:description",
        content: "Adherencia, línea de tiempo y recordatorios cariñosos para acompañar sin regañar.",
      },
    ],
  }),
  component: FamilyPage,
});

function FamilyPage() {
  const { mode, nudges, patientProfile } = useGlucoShift();

  if (mode === "cuidador") return <CaregiverDashboard />;

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-3 rounded-2xl bg-info-soft p-3">
        <Users className="mt-0.5 size-5 shrink-0 text-[oklch(0.5_0.13_240)]" />
        <p className="flex-1 text-xs text-foreground">
          Estás en el teléfono del paciente. Comparte tu código desde el botón "Vincular" para que
          tu familiar te acompañe desde su propio teléfono.
        </p>
      </div>

      <Card className="rounded-3xl border-slate-200">
        <CardHeader className="pb-2">
          <CardTitle className="font-display flex items-center gap-2 text-base">
            <Heart className="size-4 text-primary" /> Mensajes de mi familia
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {nudges.length === 0 && (
            <p className="rounded-2xl bg-slate-50 p-3 text-sm text-muted-foreground">
              Todavía no recibes mensajes. Cuando {patientProfile?.full_name ? "tu familia" : "alguien"} te
              anime, aparecerá aquí.
            </p>
          )}
          {nudges.map((n) => (
            <div key={n.id} className="rounded-2xl bg-success-soft p-3">
              <p className="text-sm text-accent-foreground">{n.message}</p>
              <p className="mt-1 text-[11px] text-muted-foreground">
                {new Date(n.created_at).toLocaleString("es-PE")}
              </p>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
