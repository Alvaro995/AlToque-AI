import { Check, Copy, Loader2, QrCode } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { supabase } from "@/integrations/supabase/client";
import { useGlucoShift } from "@/lib/glucoshift-store";
import { cn } from "@/lib/utils";

function seededQr(seed: string) {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) % 100000;
  return Array.from({ length: 21 * 21 }, (_, i) => {
    const x = i % 21;
    const y = Math.floor(i / 21);
    const inFinder = (x < 7 && y < 7) || (x > 13 && y < 7) || (x < 7 && y > 13);
    if (inFinder) {
      const lx = x > 13 ? x - 14 : x;
      const ly = y > 13 ? y - 14 : y;
      return lx === 0 || lx === 6 || ly === 0 || ly === 6 || (lx > 1 && lx < 5 && ly > 1 && ly < 5);
    }
    return (x * 7 + y * 13 + h + ((x * y) % 5)) % 3 === 0;
  });
}

function QrBlock({ value }: { value: string }) {
  const cells = seededQr(value);
  return (
    <div
      className="mx-auto grid w-44 gap-px rounded-xl bg-card p-3 ring-1 ring-border"
      style={{ gridTemplateColumns: "repeat(21, minmax(0, 1fr))" }}
      aria-hidden
    >
      {cells.map((on, i) => (
        <span
          key={i}
          className={cn("aspect-square rounded-[1px]", on ? "bg-foreground" : "bg-transparent")}
        />
      ))}
    </div>
  );
}

export function PairDialog() {
  const { mode, user, refresh, patientProfile } = useGlucoShift();
  const [open, setOpen] = useState(false);
  const [code, setCode] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  const generate = async () => {
    if (!user) return;
    setBusy(true);
    const value = String(Math.floor(100000 + Math.random() * 900000));
    const { error } = await supabase.from("invite_codes").insert({
      code: value,
      patient_id: user.id,
      expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    });
    setBusy(false);
    if (error) {
      toast.error("No se pudo generar el código");
      return;
    }
    setCode(value);
  };

  const redeem = async () => {
    setBusy(true);
    const { error } = await supabase.rpc("redeem_invite", { _code: input.trim() });
    setBusy(false);
    if (error) {
      toast.error(error.message || "Código inválido");
      return;
    }
    toast.success("¡Teléfonos vinculados! Ya ves su día en vivo 💚");
    setOpen(false);
    await refresh();
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        setOpen(v);
        if (v && mode === "paciente" && !code) void generate();
      }}
    >
      <DialogTrigger asChild>
        <Button size="sm" variant="secondary" className="gap-1.5 rounded-full">
          <QrCode className="size-4" />
          Vincular
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-[22rem] rounded-3xl">
        {mode === "paciente" ? (
          <>
            <DialogHeader>
              <DialogTitle className="font-display">Vincular a mi familiar</DialogTitle>
              <DialogDescription>
                En el otro teléfono, entra como acompañante y escribe este código.
              </DialogDescription>
            </DialogHeader>
            {code ? <QrBlock value={code} /> : null}
            <div className="rounded-2xl bg-success-soft p-4 text-center">
              <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
                Código de vinculación
              </p>
              <p className="font-display mt-1 text-3xl tracking-[0.2em] text-foreground">
                {busy ? "······" : (code ?? "······")}
              </p>
              <p className="mt-1 text-[11px] text-muted-foreground">Válido por 24 horas</p>
            </div>
            <Button
              className="w-full rounded-full"
              disabled={!code}
              onClick={() => {
                if (!code) return;
                void navigator.clipboard?.writeText(code);
                setCopied(true);
                toast.success("Código copiado");
                window.setTimeout(() => setCopied(false), 1600);
              }}
            >
              {copied ? <Check className="size-4" /> : <Copy className="size-4" />}
              {copied ? "Copiado" : "Copiar código"}
            </Button>
          </>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle className="font-display">Conectar con mi familiar</DialogTitle>
              <DialogDescription>
                {patientProfile
                  ? `Ya estás acompañando a ${patientProfile.full_name || "tu familiar"}.`
                  : "Escribe el código de 6 dígitos que aparece en el teléfono del paciente."}
              </DialogDescription>
            </DialogHeader>
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value.replace(/\D/g, "").slice(0, 6))}
              placeholder="482913"
              inputMode="numeric"
              className="rounded-2xl text-center text-2xl tracking-[0.3em]"
            />
            <Button
              className="w-full rounded-full"
              disabled={input.length !== 6 || busy}
              onClick={redeem}
            >
              {busy && <Loader2 className="size-4 animate-spin" />}
              Vincular teléfonos
            </Button>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
