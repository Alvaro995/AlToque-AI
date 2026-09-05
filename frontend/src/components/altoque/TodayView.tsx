/* Vista principal "Hoy" de AlToque AI con optimizador de secuencia de comidas y activación muscular */
import {
  CheckCircle2,
  ChefHat,
  Croissant,
  Drumstick,
  Flame,
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
import { CaregiverDashboard } from "./CaregiverDashboard";
import { useAlToque, type MealPlan } from "@/lib/altoque-store";
import { cn } from "@/lib/utils";

const GROUP_STYLES = [
  { icon: Leaf, className: "bg-success-soft text-accent-foreground ring-primary/20" },
  { icon: Drumstick, className: "bg-info-soft text-[oklch(0.45_0.12_240)] ring-[oklch(0.62_0.13_240)]/20" },
  { icon: Croissant, className: "bg-warning-soft text-warning-foreground ring-warning/30" },
];

const PRESETS = [
  "Pollo a la brasa con papas",
  "Arroz con pollo y ensalada",
  "Chaufa de pollo con wantán",
  "Menú: sopa criolla y seco de carne",
  "Pan con palta y huevo pasado",
];

const ACTIVATIONS = [
  { key: "sentadillas", label: "10 Sentadillas suaves", icon: Sparkles },
  { key: "caminata", label: "Caminata de 5 min", icon: Footprints },
  { key: "soleus", label: "Soleus Pushups sentado", icon: Timer },
];

function todayKey() {
  return new Date().toDateString();
}

export function TodayView() {
  const { mode, profile, timeline, logMeal, logActivation, planMeal } = useAlToque();
  const [where, setWhere] = useState<"casa" | "restaurante">("casa");
  const [meal, setMeal] = useState("");
  const [plan, setPlan] = useState<MealPlan | null>(null);
  const [loadingPlan, setLoadingPlan] = useState(false);
  const [checked, setChecked] = useState<number[]>([]);

  if (mode === "cuidador") return <CaregiverDashboard />;

  const todaysEvents = timeline.filter(
    (e) => new Date(e.occurred_at).toDateString() === todayKey(),
  );
  const sequenceDone = todaysEvents.some((e) => e.kind === "comida");
  const activationDone = todaysEvents.find((e) => e.kind === "movimiento");
  const streakDays = Math.max(1, new Set(timeline.map((e) => new Date(e.occurred_at).toDateString())).size);

  const buildPlan = async () => {
    const value = meal.trim();
    if (!value) {
      toast.error("Por favor introduce qué vas a comer");
      return;
    }
    setLoadingPlan(true);
    setChecked([]);
    try {
      const res = await planMeal(value, where);
      setPlan(res);
      toast.success("Secuencia calculada por el motor glucémico");
    } catch (err: any) {
      toast.error(err?.message || "Error al calcular la secuencia fisiológica");
    } finally {
      setLoadingPlan(false);
    }
  };

  const toggleCheck = (idx: number) => {
    setChecked((prev) =>
      prev.includes(idx) ? prev.filter((i) => i !== idx) : [...prev, idx],
    );
  };

  const finishMeal = async () => {
    if (!plan) return;
    try {
      const items = plan.pasos.map((p) => ({
        name: p.que,
        category: p.grupo.toLowerCase().includes("fibra")
          ? "fiber"
          : p.grupo.toLowerCase().includes("prote")
          ? "protein"
          : "carbohydrate",
      }));
      await logMeal(plan.titulo, items);
      toast.success("¡Comida registrada en tu historial clínico (+15 pts)!");
      setPlan(null);
      setMeal("");
    } catch (err: any) {
      toast.error(err?.message || "Error al registrar la comida");
    }
  };

  const finishActivation = async (actLabel: string) => {
    try {
      await logActivation(actLabel);
      toast.success("¡Activación registrada con éxito (+10 pts)!");
    } catch (err: any) {
      toast.error(err?.message || "Error al registrar la activación");
    }
  };

  return (
    <div className="space-y-4">
      {/* Banner de racha y bienvenida */}
      <div className="flex items-center justify-between rounded-3xl bg-gradient-to-r from-primary/15 via-primary/5 to-transparent p-4 border border-primary/20 shadow-sm">
        <div className="space-y-0.5">
          <p className="font-display text-sm font-semibold text-foreground">
            ¡Hola, {profile?.full_name?.split(" ")[0] || "amigo"}!
          </p>
          <p className="text-xs text-muted-foreground">
            Aplanemos tu curva hoy sin privarte de tus platos favoritos.
          </p>
        </div>
        <div className="flex items-center gap-1 rounded-full bg-warning-soft px-3 py-1.5 ring-1 ring-warning/30">
          <Flame className="size-4 text-warning-foreground fill-warning-foreground" />
          <span className="text-xs font-bold text-warning-foreground">
            {streakDays} {streakDays === 1 ? "día" : "días"}
          </span>
        </div>
      </div>

      {/* Optimizador de secuencia de plato */}
      <Card className="rounded-3xl border-slate-200 bg-white shadow-sm overflow-hidden">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="font-display flex items-center gap-2 text-base">
              <UtensilsCrossed className="size-5 text-primary" /> Secuencia del plato
            </CardTitle>
            <div className="flex rounded-full bg-slate-100 p-0.5 text-[11px] font-medium">
              <button
                type="button"
                onClick={() => setWhere("casa")}
                className={cn(
                  "rounded-full px-2.5 py-1 transition-colors",
                  where === "casa" ? "bg-white shadow text-foreground font-semibold" : "text-muted-foreground",
                )}
              >
                En casa
              </button>
              <button
                type="button"
                onClick={() => setWhere("restaurante")}
                className={cn(
                  "rounded-full px-2.5 py-1 transition-colors",
                  where === "restaurante" ? "bg-white shadow text-foreground font-semibold" : "text-muted-foreground",
                )}
              >
                Menú / Calle
              </button>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            Come lo mismo, pero en el orden correcto para reducir hasta 37% el pico de glucosa.
          </p>
        </CardHeader>

        <CardContent className="space-y-3">
          <div className="space-y-2">
            <div className="flex gap-2">
              <Input
                value={meal}
                onChange={(e) => setMeal(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && buildPlan()}
                placeholder="¿Qué vas a comer hoy? (ej. Pollo a la brasa)"
                className="rounded-2xl text-xs"
              />
              <Button
                onClick={buildPlan}
                disabled={loadingPlan || !meal.trim()}
                className="shrink-0 gap-1 rounded-2xl bg-primary text-primary-foreground"
              >
                {loadingPlan ? <Loader2 className="size-4 animate-spin" /> : <Wand2 className="size-4" />}
                Ordenar
              </Button>
            </div>

            {/* Presets peruanos rápidos */}
            <div className="flex flex-wrap gap-1.5">
              {PRESETS.map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => setMeal(p)}
                  className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] text-muted-foreground transition hover:bg-slate-200"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* Resultado del plan secuenciado */}
          {plan && (
            <div className="space-y-3 rounded-2xl bg-slate-50/80 p-3.5 border border-slate-200/80">
              <div className="flex items-center justify-between">
                <p className="font-display font-semibold text-sm text-foreground">{plan.titulo}</p>
                <Badge variant="outline" className="rounded-full bg-success-soft text-[10px] text-accent-foreground border-none">
                  Orden metabólico
                </Badge>
              </div>

              <div className="space-y-2">
                {plan.pasos.map((paso, idx) => {
                  const style = GROUP_STYLES[idx % GROUP_STYLES.length];
                  const Icon = style.icon;
                  const isChecked = checked.includes(idx);
                  return (
                    <div
                      key={idx}
                      onClick={() => toggleCheck(idx)}
                      className={cn(
                        "flex cursor-pointer items-start gap-2.5 rounded-2xl p-2.5 transition-all ring-1",
                        style.className,
                        isChecked && "opacity-60 line-through ring-0",
                      )}
                    >
                      <div className="flex size-7 shrink-0 items-center justify-center rounded-xl bg-white/80 shadow-xs">
                        {isChecked ? (
                          <CheckCircle2 className="size-4 text-primary" />
                        ) : (
                          <Icon className="size-4" />
                        )}
                      </div>
                      <div className="flex-1 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold">{paso.grupo}</span>
                          <span className="text-[10px] opacity-80">Paso {paso.orden}</span>
                        </div>
                        <p className="font-medium">{paso.que}</p>
                        <p className="text-[11px] opacity-75">{paso.porque}</p>
                      </div>
                    </div>
                  );
                })}
              </div>

              {plan.animo && (
                <p className="rounded-xl bg-white p-2.5 text-[11px] text-muted-foreground italic border border-slate-100">
                  💡 {plan.animo}
                </p>
              )}

              <Button
                onClick={finishMeal}
                className="w-full gap-2 rounded-2xl bg-primary text-primary-foreground"
              >
                <CheckCircle2 className="size-4" />
                ¡Comí en este orden! (+15 pts)
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Esponja muscular post-comida */}
      <Card className="rounded-3xl border-slate-200 bg-white shadow-sm">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="font-display flex items-center gap-2 text-base">
              <Footprints className="size-5 text-primary" /> Esponja muscular
            </CardTitle>
            {activationDone && (
              <Badge className="rounded-full bg-success-soft text-accent-foreground border-none">
                Hecho hoy ✓
              </Badge>
            )}
          </div>
          <p className="text-xs text-muted-foreground">
            20 minutos después de comer, tus músculos pueden absorber glucosa directamente sin necesidad de insulina extra.
          </p>
        </CardHeader>

        <CardContent className="space-y-2">
          <div className="grid grid-cols-3 gap-2">
            {ACTIVATIONS.map((act) => {
              const Icon = act.icon;
              return (
                <button
                  key={act.key}
                  type="button"
                  onClick={() => finishActivation(act.label)}
                  className="flex flex-col items-center gap-1.5 rounded-2xl border border-slate-100 bg-slate-50/80 p-3 text-center transition hover:border-primary/40 hover:bg-success-soft/30"
                >
                  <span className="flex size-9 items-center justify-center rounded-xl bg-white shadow-xs text-primary">
                    <Icon className="size-4" />
                  </span>
                  <span className="text-[11px] font-medium text-foreground">{act.label}</span>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Línea de tiempo de hoy */}
      <Card className="rounded-3xl border-slate-200 bg-white shadow-sm">
        <CardHeader className="pb-2">
          <CardTitle className="font-display flex items-center gap-2 text-base">
            <Sparkles className="size-4 text-primary" /> Hoy en resumen
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {todaysEvents.length === 0 ? (
            <p className="py-4 text-center text-xs text-muted-foreground">
              Aún no has registrado actividades hoy. Ordena tu almuerzo o haz 5 min de caminata para ganar tus primeros puntos.
            </p>
          ) : (
            todaysEvents.map((e) => (
              <div
                key={e.id}
                className="flex items-center justify-between rounded-2xl bg-slate-50 p-2.5 text-xs"
              >
                <div>
                  <p className="font-semibold text-foreground">{e.label}</p>
                  {e.detail && <p className="text-[11px] text-muted-foreground">{e.detail}</p>}
                </div>
                <Badge variant="outline" className="rounded-full bg-success-soft text-accent-foreground border-none font-bold">
                  +{e.points}
                </Badge>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
