/* Panel de control del acompañante familiar en AlToque AI */
import {
  Bell,
  CalendarDays,
  CheckCircle2,
  Clock,
  Heart,
  Link2,
  MessageSquare,
  Moon,
  Send,
  Sparkles,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import { useAlToque } from "@/lib/altoque-store";
import { PairDialog } from "./PairDialog";
import { cn } from "@/lib/utils";

const TEMPLATES = [
  {
    dia: "Lunes",
    titulo: "Lomo saltado familiar",
    consejo: "Sirve primero una ensalada criolla para todos y reduce el arroz a media taza. Nadie come distinto.",
  },
  {
    dia: "Miércoles",
    titulo: "Pollo al horno con verduras",
    consejo: "Verduras asadas en la misma bandeja: fibra primero sin cocinar dos menús separados.",
  },
  {
    dia: "Viernes",
    titulo: "Tallarines de casa",
    consejo: "Empieza con sopa de verduras, añade doble porción de carne y sirve la pasta al final.",
  },
];

const TONE_STYLES = {
  ok: "bg-success-soft text-accent-foreground",
  info: "bg-info-soft text-[oklch(0.45_0.12_240)]",
  warn: "bg-warning-soft text-warning-foreground",
} as const;

function hhmm(iso: string) {
  return new Date(iso).toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit" });
}

export function CaregiverDashboard() {
  const { timeline, patientProfile, hasLink, routine, sendNudge, points } = useAlToque();
  const [nudgeOpen, setNudgeOpen] = useState(false);
  const [message, setMessage] = useState(
    "Ya pasaron 20 minutos del almuerzo 💚 ¿Damos una vueltita juntos? Te acompaño por videollamada.",
  );

  const days = new Set(timeline.map((e) => new Date(e.occurred_at).toDateString()));
  const meals = timeline.filter((e) => e.kind === "comida").length;
  const moves = timeline.filter((e) => e.kind === "movimiento").length;
  const adherence = days.size === 0 ? 0 : Math.min(100, Math.round((days.size / 7) * 100));

  return (
    <div className="space-y-4">
      {/* Tarjeta de vinculación rápida si no hay link */}
      {!hasLink && (
        <Card className="rounded-3xl border-slate-200 bg-white shadow-sm">
          <CardContent className="space-y-3 pt-6 text-center">
            <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-success-soft text-primary">
              <Link2 className="size-6" />
            </span>
            <p className="font-display text-lg font-semibold text-foreground">Aún no estás vinculado</p>
            <p className="text-xs text-muted-foreground">
              Pide el código de 6 dígitos en el teléfono de tu familiar y tócalo en el botón
              "Vincular". Desde ese momento verás su día en vivo.
            </p>
            <div className="pt-1">
              <PairDialog />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Resumen del paciente vinculado */}
      <Card className="rounded-3xl border-slate-200 bg-white shadow-sm">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-3">
            <div className="flex size-12 items-center justify-center rounded-2xl bg-success-soft text-xl">
              {patientProfile?.avatar || "👨‍🦳"}
            </div>
            <div className="flex-1">
              <CardTitle className="font-display text-lg">
                {patientProfile?.full_name || "Mi familiar"}
              </CardTitle>
              <p className="text-xs text-muted-foreground">Plan de prevención · teléfonos vinculados</p>
            </div>
            <Badge className="rounded-full bg-primary text-white">{adherence}%</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Nivel de adherencia semanal</span>
              <span className="font-semibold text-primary">{adherence}%</span>
            </div>
            <Progress value={adherence} className="mt-1.5 h-2" />
          </div>

          <div className="grid grid-cols-3 gap-2 pt-1 text-center">
            <div className="rounded-2xl bg-slate-50 p-2.5">
              <p className="font-display text-lg font-bold text-foreground">{meals}</p>
              <p className="text-[10px] text-muted-foreground">Comidas guiadas</p>
            </div>
            <div className="rounded-2xl bg-slate-50 p-2.5">
              <p className="font-display text-lg font-bold text-primary">{moves}</p>
              <p className="text-[10px] text-muted-foreground">Activaciones</p>
            </div>
            <div className="rounded-2xl bg-slate-50 p-2.5">
              <p className="font-display text-lg font-bold text-warning-foreground">{points}</p>
              <p className="text-[10px] text-muted-foreground">Puntos ganados</p>
            </div>
          </div>

          <Button
            onClick={() => setNudgeOpen(true)}
            className="w-full gap-2 rounded-2xl bg-primary text-primary-foreground shadow-md shadow-primary/20"
          >
            <Heart className="size-4" /> Enviar recordatorio cariñoso
          </Button>
        </CardContent>
      </Card>

      {/* Actividad en vivo */}
      <Card className="rounded-3xl border-slate-200 bg-white shadow-sm">
        <CardHeader className="pb-2">
          <CardTitle className="font-display flex items-center gap-2 text-base">
            <Clock className="size-4 text-primary" /> Actividad de hoy en vivo
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {timeline.length === 0 ? (
            <p className="py-4 text-center text-xs text-muted-foreground">
              Aún no hay registros hoy. Cuando tu familiar registre una comida o paseo, aparecerá aquí.
            </p>
          ) : (
            timeline.slice(0, 5).map((e) => (
              <div
                key={e.id}
                className="flex items-center justify-between rounded-2xl bg-slate-50 p-3 text-xs"
              >
                <div className="space-y-0.5">
                  <p className="font-semibold text-foreground">{e.label}</p>
                  {e.detail && <p className="text-muted-foreground">{e.detail}</p>}
                </div>
                <div className="text-right">
                  <Badge variant="outline" className={cn("rounded-full border-none", TONE_STYLES[e.tone])}>
                    +{e.points} pts
                  </Badge>
                  <p className="mt-0.5 text-[10px] text-muted-foreground">{hhmm(e.occurred_at)}</p>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      {/* Menú de la semana adaptado para toda la familia */}
      <Card className="rounded-3xl border-slate-200 bg-white shadow-sm">
        <CardHeader className="pb-2">
          <CardTitle className="font-display flex items-center gap-2 text-base">
            <Sparkles className="size-4 text-primary" /> Consejos para comer juntos
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2.5">
          {TEMPLATES.map((item, i) => (
            <div key={i} className="rounded-2xl border border-slate-100 bg-slate-50/70 p-3 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-primary">{item.dia}</span>
                <span className="text-[11px] text-foreground font-medium">{item.titulo}</span>
              </div>
              <p className="mt-1 text-muted-foreground leading-relaxed">{item.consejo}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Modal para enviar recordatorio cariñoso */}
      <Dialog open={nudgeOpen} onOpenChange={setNudgeOpen}>
        <DialogContent className="max-w-sm rounded-3xl p-6">
          <DialogHeader>
            <DialogTitle className="font-display text-lg">Enviar mensaje de aliento</DialogTitle>
            <DialogDescription className="text-xs text-muted-foreground">
              Un empujoncito sin juicios para motivar a tu familiar a moverse o secuenciar su comida.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-3 pt-2">
            <Textarea
              rows={3}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="rounded-2xl text-xs"
              placeholder="Escribe un mensaje cariñoso..."
            />

            <div className="flex flex-wrap gap-1.5">
              <button
                type="button"
                onClick={() =>
                  setMessage("¡Gran trabajo con el almuerzo! 🥗 ¿Damos 5 minutos de caminata?")
                }
                className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] text-muted-foreground hover:bg-slate-200"
              >
                Caminata post-comida
              </button>
              <button
                type="button"
                onClick={() =>
                  setMessage("Recuerda tu vasito de agua antes de salir al trabajo 💧 ¡Te quiero!")
                }
                className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] text-muted-foreground hover:bg-slate-200"
              >
                Hidratación
              </button>
            </div>

            <Button
              onClick={async () => {
                if (!message.trim()) return;
                await sendNudge(message.trim());
                toast.success("Mensaje enviado con cariño 💌");
                setNudgeOpen(false);
              }}
              className="w-full gap-2 rounded-2xl"
            >
              <Send className="size-4" /> Enviar ahora
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
