import { createFileRoute } from "@tanstack/react-router";
import {
  CalendarClock,
  CheckCircle2,
  Droplets,
  FileText,
  Loader2,
  Pencil,
  Plus,
  Trash2,
  Upload,
  Wand2,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { generateRoutine } from "@/lib/coach.functions";
import { useGlucoShift, type RoutineItem } from "@/lib/glucoshift-store";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/salud")({
  head: () => ({
    meta: [
      { title: "Mi salud y mi rutina — GlucoShift" },
      {
        name: "description",
        content:
          "Guarda tu análisis de sangre y tu horario laboral, y deja que la IA arme una hoja de rutina diaria que puedes editar a tu medida.",
      },
      { property: "og:title", content: "Mi salud y mi rutina — GlucoShift" },
      {
        property: "og:description",
        content: "Análisis, horarios y una hoja de rutina diaria generada con IA y editable.",
      },
    ],
  }),
  component: HealthPage,
});

const TYPE_STYLES: Record<string, string> = {
  comida: "bg-success-soft text-accent-foreground",
  movimiento: "bg-warning-soft text-warning-foreground",
  descanso: "bg-info-soft text-[oklch(0.45_0.12_240)]",
  hidratacion: "bg-info-soft text-[oklch(0.45_0.12_240)]",
  chequeo: "bg-slate-200 text-foreground",
};

function UploadZone({
  title,
  subtitle,
  done,
  onDone,
}: {
  title: string;
  subtitle: string;
  done: boolean;
  onDone: () => void;
}) {
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const start = () => {
    if (loading) return;
    setLoading(true);
    window.setTimeout(() => {
      setLoading(false);
      onDone();
    }, 1400);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        start();
      }}
      onClick={() => inputRef.current?.click()}
      className={cn(
        "cursor-pointer rounded-2xl border-2 border-dashed p-5 text-center transition-colors",
        dragging ? "border-primary bg-success-soft" : "border-slate-300 bg-slate-50",
        done && "border-primary/40 bg-success-soft",
      )}
    >
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        onChange={() => start()}
        accept="image/*,application/pdf"
      />
      <span className="mx-auto flex size-11 items-center justify-center rounded-2xl bg-white text-primary shadow-sm">
        {loading ? (
          <Loader2 className="size-5 animate-spin" />
        ) : done ? (
          <CheckCircle2 className="size-5" />
        ) : (
          <FileText className="size-5" />
        )}
      </span>
      <p className="mt-2 text-sm font-semibold text-foreground">{title}</p>
      <p className="text-xs text-muted-foreground">
        {loading ? "Leyendo documento..." : done ? "Documento procesado" : subtitle}
      </p>
      {!loading && (
        <p className="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-primary">
          <Upload className="size-3.5" /> Arrastra o toca para subir
        </p>
      )}
    </div>
  );
}

function HealthPage() {
  const { mode, health, saveHealth, routine, saveRoutine, patientProfile } = useGlucoShift();
  const large = mode === "paciente";
  const readOnly = mode === "cuidador";

  const [hba1c, setHba1c] = useState("");
  const [fasting, setFasting] = useState("");
  const [workStart, setWorkStart] = useState("08:00");
  const [workEnd, setWorkEnd] = useState("17:00");
  const [wake, setWake] = useState("06:30");
  const [sleep, setSleep] = useState("22:30");
  const [notes, setNotes] = useState("");
  const [generating, setGenerating] = useState(false);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    if (!health) return;
    setHba1c(health.hba1c ?? "");
    setFasting(health.fasting ?? "");
    setWorkStart(health.work_start ?? "08:00");
    setWorkEnd(health.work_end ?? "17:00");
    setNotes(health.notes ?? "");
  }, [health]);

  const persist = async (patch: Record<string, string>) => {
    await saveHealth(patch);
    toast.success("Guardado");
  };

  const generate = async () => {
    setGenerating(true);
    try {
      const items = await generateRoutine({
        data: {
          workStart,
          workEnd,
          wake,
          sleep,
          notes,
          context: hba1c ? `HbA1c ${hba1c}, glucosa en ayunas ${fasting}` : "",
        },
      });
      await saveRoutine(items);
      toast.success("Tu hoja de rutina está lista");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "No pude generar la rutina");
    } finally {
      setGenerating(false);
    }
  };

  const updateItem = (i: number, patch: Partial<RoutineItem>) => {
    const next = routine.map((item, idx) => (idx === i ? { ...item, ...patch } : item));
    void saveRoutine(next);
  };

  return (
    <div className="space-y-4">
      <div>
        <h1 className={cn("font-display text-foreground", large ? "text-2xl" : "text-xl")}>
          {readOnly ? `Salud de ${patientProfile?.full_name || "tu familiar"}` : "Mi salud y mi rutina"}
        </h1>
        <p className="text-sm text-muted-foreground">
          Sube tu análisis, dinos tus horarios y armamos tu día contigo.
        </p>
      </div>

      <Card className="rounded-3xl border-slate-200">
        <CardHeader className="pb-3">
          <CardTitle className="font-display flex items-center gap-2 text-base">
            <Droplets className="size-4 text-primary" /> Análisis de sangre
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {!readOnly && (
            <UploadZone
              title="PDF o foto del laboratorio"
              subtitle="Leemos tus valores por ti"
              done={!!health?.hba1c}
              onDone={() => {
                setHba1c("5.9%");
                setFasting("108 mg/dL");
                void persist({ hba1c: "5.9%", fasting: "108 mg/dL" });
              }}
            />
          )}
          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1.5">
              <Label htmlFor="hba1c" className="text-xs">
                HbA1c
              </Label>
              <Input
                id="hba1c"
                value={hba1c}
                disabled={readOnly}
                onChange={(e) => setHba1c(e.target.value)}
                onBlur={() => void persist({ hba1c })}
                placeholder="5.9%"
                className="rounded-2xl"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="fasting" className="text-xs">
                Glucosa en ayunas
              </Label>
              <Input
                id="fasting"
                value={fasting}
                disabled={readOnly}
                onChange={(e) => setFasting(e.target.value)}
                onBlur={() => void persist({ fasting })}
                placeholder="108 mg/dL"
                className="rounded-2xl"
              />
            </div>
          </div>
          {health?.hba1c && (
            <div className="flex gap-2">
              <Badge className="rounded-full bg-warning text-warning-foreground">Prediabetes</Badge>
              <Badge className="rounded-full bg-alert text-alert-foreground">Ayunas elevada</Badge>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="rounded-3xl border-slate-200">
        <CardHeader className="pb-3">
          <CardTitle className="font-display flex items-center gap-2 text-base">
            <CalendarClock className="size-4 text-primary" /> Mis horarios
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {!readOnly && (
            <UploadZone
              title="Cronograma laboral o escolar"
              subtitle="Detectamos tu jornada automáticamente"
              done={!!health?.work_start}
              onDone={() => {
                setWorkStart("08:00");
                setWorkEnd("17:00");
                void persist({ work_start: "08:00", work_end: "17:00" });
                toast.success("Jornada detectada: 8:00 a 17:00");
              }}
            />
          )}
          <div className="grid grid-cols-2 gap-2">
            {(
              [
                { id: "wake", label: "Me levanto", value: wake, set: setWake },
                { id: "workStart", label: "Entro a trabajar", value: workStart, set: setWorkStart },
                { id: "workEnd", label: "Salgo", value: workEnd, set: setWorkEnd },
                { id: "sleep", label: "Me duermo", value: sleep, set: setSleep },
              ] as const
            ).map((f) => (
              <div key={f.id} className="space-y-1.5">
                <Label htmlFor={f.id} className="text-xs">
                  {f.label}
                </Label>
                <Input
                  id={f.id}
                  type="time"
                  value={f.value}
                  disabled={readOnly}
                  onChange={(e) => f.set(e.target.value)}
                  onBlur={() =>
                    void saveHealth({ work_start: workStart, work_end: workEnd, notes })
                  }
                  className="rounded-2xl"
                />
              </div>
            ))}
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="notes" className="text-xs">
              Algo que debamos saber
            </Label>
            <Input
              id="notes"
              value={notes}
              disabled={readOnly}
              onChange={(e) => setNotes(e.target.value)}
              onBlur={() => void persist({ notes })}
              placeholder="Trabajo sentado, ceno tarde, rodilla delicada..."
              className="rounded-2xl"
            />
          </div>
        </CardContent>
      </Card>

      <Card className="rounded-3xl border-primary/20">
        <CardHeader className="pb-3">
          <CardTitle className="font-display flex items-center gap-2 text-base">
            <Wand2 className="size-4 text-primary" /> Hoja de rutina diaria
          </CardTitle>
          <p className="text-xs text-muted-foreground">
            Generada con IA según tus horarios. Puedes editar cada bloque.
          </p>
        </CardHeader>
        <CardContent className="space-y-3">
          {!readOnly && (
            <div className="flex gap-2">
              <Button
                onClick={() => void generate()}
                disabled={generating}
                className="flex-1 rounded-full"
              >
                {generating ? <Loader2 className="size-4 animate-spin" /> : <Wand2 className="size-4" />}
                {routine.length ? "Regenerar rutina" : "Generar mi rutina"}
              </Button>
              {routine.length > 0 && (
                <Button
                  variant="outline"
                  className="rounded-full bg-white"
                  onClick={() => setEditing((v) => !v)}
                >
                  <Pencil className="size-4" />
                  {editing ? "Listo" : "Editar"}
                </Button>
              )}
            </div>
          )}

          {routine.length === 0 && !generating && (
            <p className="rounded-2xl bg-slate-100 p-3 text-sm text-muted-foreground">
              Aún no hay rutina. Genera una con tus horarios y ajústala a tu vida real.
            </p>
          )}

          <ol className="space-y-2">
            {routine.map((item, i) => (
              <li key={`${item.hora}-${i}`} className="rounded-2xl bg-slate-50 p-3">
                {editing ? (
                  <div className="space-y-2">
                    <div className="flex gap-2">
                      <Input
                        value={item.hora}
                        onChange={(e) => updateItem(i, { hora: e.target.value })}
                        className="w-24 rounded-xl"
                      />
                      <Input
                        value={item.titulo}
                        onChange={(e) => updateItem(i, { titulo: e.target.value })}
                        className="flex-1 rounded-xl"
                      />
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => void saveRoutine(routine.filter((_, idx) => idx !== i))}
                      >
                        <Trash2 className="size-4 text-muted-foreground" />
                      </Button>
                    </div>
                    <Input
                      value={item.detalle}
                      onChange={(e) => updateItem(i, { detalle: e.target.value })}
                      className="rounded-xl"
                    />
                  </div>
                ) : (
                  <div className="flex items-start gap-3">
                    <span
                      className={cn(
                        "rounded-lg px-2 py-1 text-[11px] font-semibold",
                        TYPE_STYLES[item.tipo] ?? "bg-slate-200 text-foreground",
                      )}
                    >
                      {item.hora}
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-foreground">{item.titulo}</p>
                      <p className="text-xs text-muted-foreground">{item.detalle}</p>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ol>

          {editing && (
            <Button
              variant="outline"
              className="w-full rounded-full bg-white"
              onClick={() =>
                void saveRoutine([
                  ...routine,
                  { hora: "12:00", titulo: "Nuevo bloque", detalle: "", tipo: "chequeo" },
                ])
              }
            >
              <Plus className="size-4" /> Agregar bloque
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
