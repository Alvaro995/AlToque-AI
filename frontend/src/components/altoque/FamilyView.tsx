/* Vista "Familia" en AlToque AI con red de apoyo, recordatorios cariñosos y vinculación */
import {
  Heart,
  MessageCircle,
  QrCode,
  Share2,
  Smile,
  Sparkles,
  Users,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CaregiverDashboard } from "./CaregiverDashboard";
import { PairDialog } from "./PairDialog";
import { useAlToque } from "@/lib/altoque-store";

export function FamilyView() {
  const { mode, nudges, patientProfile, hasLink } = useAlToque();
  const [replied, setReplied] = useState<string[]>([]);

  if (mode === "cuidador") return <CaregiverDashboard />;

  const handleQuickReply = (id: string, emoji: string) => {
    setReplied((prev) => [...prev, id]);
    toast.success(`Respuesta "${emoji}" enviada a tu familiar 💚`);
  };

  return (
    <div className="space-y-4">
      {/* Banner de vinculación familiar */}
      <div className="flex items-start gap-3 rounded-3xl bg-info-soft p-4 border border-info/20 shadow-sm">
        <Users className="mt-0.5 size-5 shrink-0 text-[oklch(0.5_0.13_240)]" />
        <div className="flex-1 space-y-1">
          <p className="text-xs font-semibold text-foreground">
            Acompañamiento familiar en dos celulares
          </p>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Tu familiar puede seguir tu progreso y enviarte mensajes cariñosos sin invadir tu día ni juzgarte.
          </p>
          <div className="pt-2">
            <PairDialog />
          </div>
        </div>
      </div>

      {/* Mensajes cariñosos recibidos de la familia */}
      <Card className="rounded-3xl border-slate-200 bg-white shadow-sm">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="font-display flex items-center gap-2 text-base">
              <Heart className="size-4 text-primary fill-primary/20" /> Mensajes de mi familia
            </CardTitle>
            <Badge variant="outline" className="rounded-full bg-success-soft text-[10px] text-accent-foreground border-none">
              {nudges.length} mensajes
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-2.5">
          {nudges.length === 0 ? (
            <p className="py-4 text-center text-xs text-muted-foreground">
              Aún no has recibido mensajes de tu acompañante familiar.
            </p>
          ) : (
            nudges.map((n) => {
            const isReplied = replied.includes(n.id);
            return (
              <div
                key={n.id}
                className="space-y-2 rounded-2xl bg-success-soft/70 p-3.5 border border-primary/15"
              >
                <p className="text-xs text-foreground leading-relaxed font-medium">{n.message}</p>
                <div className="flex items-center justify-between pt-1 text-[11px] text-muted-foreground">
                  <span>{new Date(n.created_at).toLocaleString("es-PE", { dateStyle: "short", timeStyle: "short" })}</span>
                  {isReplied ? (
                    <span className="text-primary font-semibold">Respuesta enviada ✓</span>
                  ) : (
                    <div className="flex gap-1.5">
                      <button
                        type="button"
                        onClick={() => handleQuickReply(n.id, "💚")}
                        className="rounded-full bg-white px-2 py-0.5 shadow-xs hover:bg-slate-50 transition"
                      >
                        💚
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickReply(n.id, "🚶‍♂️ Listo!")}
                        className="rounded-full bg-white px-2 py-0.5 shadow-xs hover:bg-slate-50 transition"
                      >
                        🚶‍♂️ Listo!
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickReply(n.id, "Gracias!")}
                        className="rounded-full bg-white px-2 py-0.5 shadow-xs hover:bg-slate-50 transition"
                      >
                        🥰
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          }))}
        </CardContent>
      </Card>

      {/* Tarjeta de impacto del acompañamiento */}
      <Card className="rounded-3xl border-slate-200 bg-white shadow-sm">
        <CardHeader className="pb-2">
          <CardTitle className="font-display flex items-center gap-2 text-base">
            <Sparkles className="size-4 text-primary" /> ¿Por qué en familia?
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-xs text-muted-foreground leading-relaxed">
          <p>
            Los estudios demuestran que las personas que cuentan con el apoyo cariñoso de un familiar tienen un
            <strong className="text-foreground"> 64% mayor éxito</strong> en mantener hábitos preventivos a largo plazo sin recaídas.
          </p>
          <div className="rounded-2xl bg-slate-50 p-3 border border-slate-100">
            <p className="font-semibold text-foreground">Regla de oro AlToque:</p>
            <p className="mt-0.5">
              Cero regaños, cero culpas. Solo recordatorios positivos como salir a caminar juntos o disfrutar la ensalada primero.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
