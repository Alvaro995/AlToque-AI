import { createFileRoute } from "@tanstack/react-router";
import {
  ChefHat,
  CheckCircle2,
  Croissant,
  Drumstick,
  Footprints,
  Heart,
  Leaf,
  Loader2,
  Sparkles,
  Timer,
  UtensilsCrossed,
  Wand2,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { CaregiverDashboard } from "@/components/glucoshift/CaregiverDashboard";
import { planMeal, type MealPlan } from "@/lib/coach.functions";
import { useGlucoShift } from "@/lib/glucoshift-store";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "GlucoShift — Revierte la prediabetes en familia" },
      {
        name: "description",
        content:
          "GlucoShift acompaña a pacientes y familias con secuencia de comidas guiada por IA, activación muscular post-comida y un coach empático para mantener la curva de glucosa plana.",
      },
      { property: "og:title", content: "GlucoShift — Revierte la prediabetes en familia" },
      {
        property: "og:description",
        content:
          "Orden del plato con IA, esponja muscular y acompañamiento familiar en dos teléfonos.",
      },
    ],
  }),
  component: TodayPage,
});

const GROUP_STYLES = [
  { icon: Leaf, className: "bg-success-soft text-accent-foreground ring-primary/20" },
  { icon: Drumstick, className: "bg-info-soft text-[oklch(0.45_0.12_240)] ring-[oklch(0.62_0.13_240)]/20" },
  { icon: Croissant, className: "bg-warning-soft text-warning-foreground ring-warning/30" },
];

const PRESETS = [
  "Pollo a la brasa con papas",
  "Arroz con pollo y ensalada",
  "Chaufa de pollo",
  "Menú: sopa, seco con frejoles",
  "Pan con palta y café",
];

const ACTIVATIONS = [
  { key: "sentadillas", label: "10 Sentadillas suaves", icon: Sparkles },
  { key: "caminata", label: "Caminata de 5 min", icon: Footprints },
  { key: "soleus", label: "Soleus Pushups sentado", icon: Timer },
];

function todayKey() {
  return new Date().toDateString();
}

function TodayPage() {
  const { mode, profile, timeline, health, nudges, logEvent } = useGlucoShift();
  const [where, setWhere] = useState<"casa" | "restaurante">("casa");
  const [meal, setMeal] = useState("");
  const [plan, setPlan] = useState<MealPlan | null>(null);
  const [loadingPlan, setLoadingPlan] = useState(false);
  const [checked, setChecked] = useState<number[]>([]);
  const large = mode === "paciente";

  if (mode === "cuidador") return <CaregiverDashboard />;

  const todaysEvents = timeline.filter(
    (e) => new Date(e.occurred_at).toDateString() === todayKey(),
  );
  const sequenceDone = todaysEvents.some((e) => e.kind === "comida");
  const activationDone = todaysEvents.find((e) => e.kind === "movimiento");
  const streakDays = new Set(timeline.map((e) => new Date(e.occurred_at).toDateString())).size;

  const build = async () => {
    const value = meal.trim();
    if (!value) {
      toast.error("Cuéntame qué vas a comer");
      return;
    }
    setLoadingPlan(true);
    setChecked([]);
    try {
      const context = health?.hba1c ? `HbA1c ${health.hba1c}, ayunas ${health.fasting ?? "-"}` : "";
      const result = await planMeal({ data: { meal: value, place: where, context } });
      setPlan(result);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "No pude armar el orden");
    } finally {
      setLoadingPlan(false);
    }
  };

  const confirm = async () => {
    if (sequenceDone) return;
    await logEvent({
      kind: "comida",
      label: plan?.titulo ? `Comida registrada: ${plan.titulo}` : "Comida registrada",
      detail: "Orden correcto: fibra → proteína → carbohidrato",
      points: 15,
      tone: "ok",
    });
    toast.success("¡+15 pts Curva Plana! Comiste en el orden correcto 💚");
  };

  const completeActivation = async (label: string) => {
    if (activationDone) return;
    await logEvent({
      kind: "movimiento",
      label: "Esponja muscular activada",
      detail: label,
      points: 10,
      tone: "ok",
    });
    toast.success(`¡Genial! ${label} completado. Tus músculos absorben la glucosa 🦵`);
  };

  const lastNudge = nudges[0];

  return (
    <div className="space-y-4">
      <section className="rounded-3xl bg-gradient-to-br from-primary to-[oklch(0.62_0.14_178)] p-5 text-primary-foreground shadow-lg shadow-primary/20">
        <p className="text-sm opacity-90">Hola, {profile?.full_name?.split(" ")[0] || "amigo"} 👋</p>
        <h1 className={cn("font-display mt-1 leading-snug", large ? "text-2xl" : "text-xl")}>
          Hoy tu curva va plana. Sigamos así, un paso a la vez.
        </h1>
        <div className="mt-4 rounded-2xl bg-white/15 p-3">
          <div className="flex justify-between text-xs">
            <span>Días con registro</span>
            <span className="font-semibold">{streakDays} de 7</span>
          </div>
          <Progress value={Math.min(100, (streakDays / 7) * 100)} className="mt-2 h-2 bg-white/25" />
        </div>
      </section>

      {lastNudge && (
        <div className="flex items-start gap-3 rounded-2xl border border-primary/20 bg-success-soft p-3">
          <Heart className="mt-0.5 size-4 shrink-0 text-primary" />
          <p className="text-sm text-accent-foreground">{lastNudge.message}</p>
        </div>
      )}

      <Card className="rounded-3xl border-slate-200">
        <CardHeader className="pb-3">
          <CardTitle className={cn("font-display", large ? "text-xl" : "text-lg")}>
            ¿Qué vas a comer hoy?
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Escribe tu plato real y la IA te dice en qué orden comerlo. Mismo plato, cero pico.
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex rounded-full bg-slate-100 p-1">
            {(
              [
                { key: "casa", label: "En casa", icon: ChefHat },
                { key: "restaurante", label: "En restaurante", icon: UtensilsCrossed },
              ] as const
            ).map((opt) => {
              const Icon = opt.icon;
              return (
                <button
                  key={opt.key}
                  type="button"
                  onClick={() => setWhere(opt.key)}
                  className={cn(
                    "flex flex-1 items-center justify-center gap-1.5 rounded-full py-2 text-sm font-semibold transition-all",
                    where === opt.key ? "bg-white text-primary shadow-sm" : "text-muted-foreground",
                  )}
                >
                  <Icon className="size-4" />
                  {opt.label}
                </button>
              );
            })}
          </div>

          <form
            className="flex gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              void build();
            }}
          >
            <Input
              value={meal}
              onChange={(e) => setMeal(e.target.value)}
              placeholder="Ej. pollo a la brasa con papas y gaseosa"
              className="rounded-2xl bg-slate-100"
            />
            <Button type="submit" disabled={loadingPlan} className="shrink-0 rounded-2xl">
              {loadingPlan ? <Loader2 className="size-4 animate-spin" /> : <Wand2 className="size-4" />}
              Ordenar
            </Button>
          </form>

          <div className="flex gap-2 overflow-x-auto pb-1">
            {PRESETS.map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setMeal(p)}
                className="shrink-0 rounded-full bg-slate-100 px-3 py-1.5 text-xs font-medium text-muted-foreground"
              >
                {p}
              </button>
            ))}
          </div>

          {loadingPlan && (
            <p className="flex items-center gap-2 rounded-2xl bg-slate-100 p-3 text-sm text-muted-foreground">
              <Loader2 className="size-4 animate-spin" /> Armando tu orden anti-pico...
            </p>
          )}

          {plan && !loadingPlan && (
            <div className="space-y-3">
              <p className="text-sm font-semibold text-foreground">{plan.titulo}</p>
              <ol className="space-y-2">
                {plan.pasos.map((step, i) => {
                  const style = GROUP_STYLES[Math.min(i, GROUP_STYLES.length - 1)]!;
                  const Icon = style.icon;
                  const isChecked = checked.includes(i);
                  return (
                    <li key={`${step.grupo}-${i}`}>
                      <button
                        type="button"
                        onClick={() =>
                          setChecked((c) =>
                            c.includes(i) ? c.filter((k) => k !== i) : [...c, i],
                          )
                        }
                        className={cn(
                          "flex w-full items-start gap-3 rounded-2xl p-3 text-left ring-1 transition-all",
                          style.className,
                          isChecked ? "ring-2" : "opacity-95",
                        )}
                      >
                        <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-white/70">
                          <Icon className="size-5" />
                        </span>
                        <span className="min-w-0 flex-1">
                          <span
                            className={cn(
                              "block font-semibold",
                              large ? "text-base" : "text-sm",
                              isChecked && "line-through",
                            )}
                          >
                            {i + 1}. {step.grupo}
                          </span>
                          <span className="block text-xs opacity-90">{step.que}</span>
                          <span className="mt-0.5 block text-[11px] opacity-70">{step.porque}</span>
                        </span>
                        {isChecked && <CheckCircle2 className="size-5 shrink-0" />}
                      </button>
                    </li>
                  );
                })}
              </ol>
              <div className="rounded-2xl bg-slate-100 p-3">
                <p className="text-xs font-semibold text-foreground">Después de comer</p>
                <p className="text-sm text-muted-foreground">{plan.movimiento}</p>
              </div>
              <p className="text-sm text-primary">{plan.animo}</p>
            </div>
          )}

          <Button
            onClick={() => void confirm()}
            disabled={sequenceDone}
            size={large ? "lg" : "default"}
            className="w-full rounded-full text-sm font-semibold"
          >
            <CheckCircle2 className="size-4" />
            {sequenceDone
              ? "¡Registrado hoy! +15 pts Curva Plana"
              : "Comí en el orden correcto (+15 pts)"}
          </Button>
        </CardContent>
      </Card>

      <Card className="rounded-3xl border-warning/30 bg-warning-soft">
        <CardHeader className="pb-2">
          <Badge className="w-fit rounded-full bg-warning text-warning-foreground">
            Esponja muscular
          </Badge>
          <CardTitle className={cn("font-display", large ? "text-xl" : "text-lg")}>
            20 minutos después de comer
          </CardTitle>
          <p className="text-sm text-warning-foreground/80">
            Es hora de activar tus músculos. Bastan unos minutos para bajar el pico.
          </p>
        </CardHeader>
        <CardContent className="space-y-2">
          {ACTIVATIONS.map((a) => {
            const Icon = a.icon;
            const done = activationDone?.detail === a.label;
            return (
              <button
                key={a.key}
                type="button"
                onClick={() => void completeActivation(a.label)}
                className={cn(
                  "flex w-full items-center gap-3 rounded-2xl bg-white p-3 text-left ring-1 ring-warning/20 transition-all active:scale-[0.99]",
                  done && "ring-2 ring-primary",
                )}
              >
                <span
                  className={cn(
                    "flex size-9 items-center justify-center rounded-xl",
                    done
                      ? "bg-primary text-primary-foreground"
                      : "bg-warning-soft text-warning-foreground",
                  )}
                >
                  {done ? <CheckCircle2 className="size-5" /> : <Icon className="size-5" />}
                </span>
                <span
                  className={cn(
                    "flex-1 font-semibold text-foreground",
                    large ? "text-base" : "text-sm",
                  )}
                >
                  {a.label}
                </span>
                {done && (
                  <span className="animate-in zoom-in text-xs font-semibold text-primary">
                    +10 pts
                  </span>
                )}
              </button>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}
