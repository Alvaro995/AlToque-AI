import { Bell, CalendarDays, CheckCircle2, Clock, Heart, Link2, MessageSquare, Moon } from "lucide-react";
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
import { useGlucoShift } from "@/lib/glucoshift-store";
import { cn } from "@/lib/utils";

const TEMPLATES = [
  {
    day: "Lunes",
    title: "Lomo saltado familiar",
    tip: "Sirve primero una ensalada criolla para todos y reduce el arroz a media taza. Nadie come distinto.",
  },
  {
    day: "Miércoles",
    title: "Pollo al horno con verduras",
    tip: "Verduras asadas en la misma bandeja: fibra primero sin cocinar dos menús.",
  },
  {
    day: "Viernes",
    title: "Tallarines de casa",
    tip: "Empieza con sopa de verduras, añade doble porción de carne y sirve la pasta al final.",
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
  const { mode, timeline, patientProfile, patientId, routine, sendNudge, points } = useGlucoShift();
  const [nudgeOpen, setNudgeOpen] = useState(false);
  const [message, setMessage] = useState(
    "Ya pasaron 20 minutos del almuerzo 💚 ¿Damos una vueltita juntos? Te acompaño por videollamada.",
  );

  if (mode === "cuidador" && !patientId) {
    return (
      <Card className="rounded-3xl border-slate-200">
        <CardContent className="space-y-3 pt-6 text-center">
          <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-success-soft text-primary">
            <Link2 className="size-6" />
          </span>
          <p className="font-display text-lg text-foreground">Aún no estás vinculado</p>
          <p className="text-sm text-muted-foreground">
            Pide el código de 6 dígitos en el teléfono de tu familiar y tócalo en el botón
            "Vincular" de arriba. Desde ese momento verás su día en vivo.
          </p>
        </CardContent>
      </Card>
    );
  }

  const days = new Set(timeline.map((e) => new Date(e.occurred_at).toDateString()));
  const meals = timeline.filter((e) => e.kind === "comida").length;
  const moves = timeline.filter((e) => e.kind === "movimiento").length;
  const adherence = Math.min(100, Math.round((days.size / 7) * 100));

  return (
    <div className="space-y-4">
      <Card className="rounded-3xl border-slate-200">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-3">
            <div className="flex size-12 items-center justify-center rounded-2xl bg-success-soft text-xl">
              {patientProfile?.avatar || "👨‍🦳"}
            </div>
            <div className="flex-1">
              <CardTitle className="font-display text-lg">
                {patientProfile?.full_name || "Mi familiar"}
              </CardTitle>
              <p className="text-xs text-muted-foreground">Prediabetes · teléfonos vinculados</p>
            </div>
            <Badge className="rounded-full bg-primary">{adherence}%</Badge>
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
          <div className="grid grid-cols-3 gap-2 text-center">
            {[
              { label: "Orden OK", value: `${meals}`, icon: CheckCircle2 },
              { label: "Movimiento", value: `${moves}`, icon: Heart },
              { label: "Puntos", value: `${points}`, icon: Moon },
            ].map((s) => {
              const Icon = s.icon;
              return (
                <div key={s.label} className="rounded-2xl bg-slate-100 p-3">
                  <Icon className="mx-auto size-4 text-primary" />
                  <p className="mt-1 text-sm font-semibold text-foreground">{s.value}</p>
                  <p className="text-[11px] text-muted-foreground">{s.label}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <Card className="rounded-3xl border-slate-200">
        <CardHeader className="pb-2">
          <CardTitle className="font-display flex items-center gap-2 text-base">
            <Clock className="size-4 text-primary" /> Línea de tiempo en vivo
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {timeline.length === 0 && (
            <p className="rounded-2xl bg-slate-50 p-3 text-sm text-muted-foreground">
              Todavía no hay actividades registradas hoy.
            </p>
          )}
          {timeline.slice(0, 12).map((e) => (
            <div key={e.id} className="flex items-start gap-3 rounded-2xl bg-slate-50 p-3">
              <span
                className={cn(
                  "mt-0.5 rounded-lg px-2 py-1 text-[11px] font-semibold",
                  TONE_STYLES[e.tone] ?? TONE_STYLES.ok,
                )}
              >
                {hhmm(e.occurred_at)}
              </span>
              <div className="min-w-0">
                <p className="text-sm font-semibold text-foreground">{e.label}</p>
                <p className="text-xs text-muted-foreground">{e.detail}</p>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {routine.length > 0 && (
        <Card className="rounded-3xl border-slate-200">
          <CardHeader className="pb-2">
            <CardTitle className="font-display flex items-center gap-2 text-base">
              <CalendarDays className="size-4 text-primary" /> Su rutina de hoy
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {routine.slice(0, 6).map((item, i) => (
              <div key={`${item.hora}-${i}`} className="flex gap-3 rounded-2xl bg-slate-50 p-3">
                <span className="text-xs font-semibold text-primary">{item.hora}</span>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-foreground">{item.titulo}</p>
                  <p className="text-xs text-muted-foreground">{item.detalle}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card className="rounded-3xl border-primary/20 bg-success-soft">
        <CardContent className="space-y-3 pt-6">
          <p className="text-sm text-accent-foreground">
            Un recordatorio cariñoso funciona mejor que un regaño. Le llegará a su teléfono al
            instante.
          </p>
          <Button className="w-full rounded-full" onClick={() => setNudgeOpen(true)}>
            <MessageSquare className="size-4" />
            Enviar recordatorio cariñoso
          </Button>
          <Button
            variant="outline"
            className="w-full rounded-full bg-white"
            onClick={() => toast.success("Alerta suave programada para las 20:00 🌙")}
          >
            <Bell className="size-4" />
            Programar aviso de caminata nocturna
          </Button>
        </CardContent>
      </Card>

      <Card className="rounded-3xl border-slate-200">
        <CardHeader className="pb-2">
          <CardTitle className="font-display flex items-center gap-2 text-base">
            <CalendarDays className="size-4 text-primary" /> Plantillas familiares de la semana
          </CardTitle>
          <p className="text-xs text-muted-foreground">
            Un solo menú para toda la familia, sin cocinar aparte.
          </p>
        </CardHeader>
        <CardContent className="space-y-2">
          {TEMPLATES.map((t) => (
            <div key={t.day} className="rounded-2xl bg-slate-50 p-3">
              <p className="text-xs font-semibold text-primary uppercase">{t.day}</p>
              <p className="text-sm font-semibold text-foreground">{t.title}</p>
              <p className="text-xs text-muted-foreground">{t.tip}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      <Dialog open={nudgeOpen} onOpenChange={setNudgeOpen}>
        <DialogContent className="max-w-[22rem] rounded-3xl">
          <DialogHeader>
            <DialogTitle className="font-display">
              Recordatorio para {patientProfile?.full_name?.split(" ")[0] || "tu familiar"}
            </DialogTitle>
            <DialogDescription>Aparecerá en su pantalla de inicio al instante.</DialogDescription>
          </DialogHeader>
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={4}
            className="rounded-2xl"
          />
          <Button
            className="w-full rounded-full"
            onClick={async () => {
              await sendNudge(message);
              setNudgeOpen(false);
              toast.success("Mensaje enviado 💚");
            }}
          >
            Enviar ahora
          </Button>
        </DialogContent>
      </Dialog>
    </div>
  );
}
