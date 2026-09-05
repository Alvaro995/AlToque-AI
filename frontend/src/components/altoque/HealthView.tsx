/* Vista "Mi salud y rutina" en AlToque AI con ingesta de análisis de sangre, horarios y rutina con IA */
import {
  CalendarClock,
  CheckCircle2,
  Clock,
  Droplets,
  FileText,
  HeartPulse,
  Loader2,
  Pencil,
  Plus,
  Save,
  Trash2,
  Upload,
  Wand2,
} from "lucide-react";
import { useRef, useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAlToque, type RoutineItem } from "@/lib/altoque-store";
import { cn } from "@/lib/utils";

const TYPE_STYLES: Record<string, string> = {
  comida: "bg-success-soft text-accent-foreground",
  movimiento: "bg-warning-soft text-warning-foreground",
  descanso: "bg-info-soft text-[oklch(0.45_0.12_240)]",
  hidratacion: "bg-info-soft text-[oklch(0.45_0.12_240)]",
  chequeo: "bg-slate-200 text-foreground",
};

export function HealthView() {
  const { health, routine, uploadLabFile, saveSleepTarget } = useAlToque();
  const [hba1c, setHba1c] = useState(health?.hba1c || "");
  const [fasting, setFasting] = useState(health?.fasting || "");
  const [workStart, setWorkStart] = useState(health?.work_start || "08:30");
  const [workEnd, setWorkEnd] = useState(health?.work_end || "18:00");
  const [wake, setWake] = useState("06:30");
  const [sleep, setSleep] = useState("23:00");
  const [generating, setGenerating] = useState(false);
  const [uploadDone, setUploadDone] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      await uploadLabFile(file);
      setUploadDone(true);
      toast.success(`Documento "${file.name}" cargado y enviado al motor OCR`);
    } catch (err: any) {
      toast.error(err?.message || "Error al subir el archivo al backend");
    } finally {
      setUploading(false);
    }
  };

  const handleSaveSchedule = async () => {
    setGenerating(true);
    try {
      await saveSleepTarget(sleep, wake);
      toast.success("Ventanas metabólicas y ciclo circadiano conciliados");
    } catch (err: any) {
      toast.error(err?.message || "Error al actualizar metas de sueño");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Tarjeta de análisis de sangre y valores clínicos */}
      <Card className="rounded-3xl border-slate-200 bg-white shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="font-display flex items-center gap-2 text-base">
            <Droplets className="size-5 text-primary" /> Mis valores de laboratorio
          </CardTitle>
          <p className="text-xs text-muted-foreground">
            Sube tu orden de laboratorio o ingresa tus resultados para calibrar tu copiloto.
          </p>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* Zona de carga */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className={cn(
              "flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-4 text-center transition hover:border-primary/50",
              uploadDone ? "border-primary/40 bg-success-soft/30" : "border-slate-200 bg-slate-50/60",
            )}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleUpload(f);
              }}
            />
            {uploading ? (
              <Loader2 className="size-6 animate-spin text-primary" />
            ) : uploadDone ? (
              <CheckCircle2 className="size-6 text-primary" />
            ) : (
              <Upload className="size-6 text-muted-foreground" />
            )}
            <p className="mt-1 text-xs font-semibold text-foreground">
              {uploadDone ? "Documento procesado por motor OCR" : "Subir PDF o foto de examen"}
            </p>
            <p className="text-[10px] text-muted-foreground">
              Extrae automáticamente HbA1c, glucosa basal y perfil lipídico
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-1">
            <div className="space-y-1">
              <Label className="text-xs">Hemoglobina glicosilada (HbA1c)</Label>
              <div className="relative">
                <Input
                  value={hba1c || (health?.hba1c ?? "")}
                  onChange={(e) => setHba1c(e.target.value)}
                  placeholder="Pendiente de análisis"
                  className="rounded-2xl text-xs pr-7"
                />
                <span className="absolute right-2.5 top-2.5 text-[10px] text-muted-foreground">%</span>
              </div>
            </div>

            <div className="space-y-1">
              <Label className="text-xs">Glucosa en ayunas</Label>
              <div className="relative">
                <Input
                  value={fasting || (health?.fasting ?? "")}
                  onChange={(e) => setFasting(e.target.value)}
                  placeholder="Pendiente de análisis"
                  className="rounded-2xl text-xs pr-11"
                />
                <span className="absolute right-2.5 top-2.5 text-[10px] text-muted-foreground">mg/dL</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Horario y turnos laborales */}
      <Card className="rounded-3xl border-slate-200 bg-white shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="font-display flex items-center gap-2 text-base">
            <Clock className="size-5 text-primary" /> Mi jornada y descanso circadiano
          </CardTitle>
          <p className="text-xs text-muted-foreground">
            Sincroniza tus metas de sueño con el motor circadiano para calcular tus ventanas metabólicas.
          </p>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label className="text-xs">Hora de despertar</Label>
              <Input
                type="time"
                value={wake}
                onChange={(e) => setWake(e.target.value)}
                className="rounded-2xl text-xs"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Hora de dormir</Label>
              <Input
                type="time"
                value={sleep}
                onChange={(e) => setSleep(e.target.value)}
                className="rounded-2xl text-xs"
              />
            </div>
          </div>

          <Button
            onClick={handleSaveSchedule}
            disabled={generating}
            className="w-full gap-2 rounded-2xl bg-primary text-primary-foreground"
          >
            {generating ? <Loader2 className="size-4 animate-spin" /> : <Save className="size-4" />}
            Sincronizar cronobiología con el servidor
          </Button>
        </CardContent>
      </Card>

      {/* Hoja de rutina diaria editable */}
      <Card className="rounded-3xl border-slate-200 bg-white shadow-sm">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="font-display flex items-center gap-2 text-base">
              <CalendarClock className="size-5 text-primary" /> Ventanas metabólicas conciliadas
            </CardTitle>
            <Badge variant="outline" className="rounded-full bg-success-soft text-accent-foreground border-none text-[10px]">
              {routine.length} ventanas
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground">
            Ventanas calculadas por el algoritmo circadiano para ingesta óptima.
          </p>
        </CardHeader>
        <CardContent className="space-y-2">
          {routine.length === 0 ? (
            <p className="py-4 text-center text-xs text-muted-foreground">
              Aún no hay ventanas metabólicas calculadas. Pulsa "Sincronizar cronobiología" para calcularlas.
            </p>
          ) : (
            routine.map((item, idx) => (
              <div
                key={idx}
                className="flex items-start gap-2.5 rounded-2xl bg-slate-50/80 p-2.5 text-xs border border-slate-100"
              >
                <span className="shrink-0 font-mono text-[11px] font-bold text-primary mt-0.5">
                  {item.hora}
                </span>
                <div className="flex-1 space-y-0.5">
                  <div className="flex items-center justify-between">
                    <p className="font-semibold text-foreground">{item.titulo}</p>
                    <span
                      className={cn(
                        "rounded-full px-2 py-0.5 text-[9px] font-semibold uppercase tracking-wider",
                        TYPE_STYLES[item.tipo] || "bg-slate-200 text-foreground",
                      )}
                    >
                      {item.tipo}
                    </span>
                  </div>
                  <p className="text-[11px] text-muted-foreground">{item.detalle}</p>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
