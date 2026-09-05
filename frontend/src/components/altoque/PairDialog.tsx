/* Diálogo para vincular paciente y acompañante familiar mediante el backend de AlToque AI */
import { Check, Copy, Link2, Mail, Users } from "lucide-react";
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
import { Label } from "@/components/ui/label";
import { useAlToque } from "@/lib/altoque-store";
import { peticionApi } from "@/lib/api-client";

export function PairDialog() {
  const { mode, profile, refreshAll } = useAlToque();
  const [open, setOpen] = useState(false);
  const [emailInput, setEmailInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  const handlePairCaregiver = async () => {
    const trimmed = emailInput.trim();
    if (!trimmed.includes("@")) {
      toast.error("Por favor introduce un correo electrónico válido");
      return;
    }
    setBusy(true);
    try {
      await peticionApi("/api/v1/care-network/pairings", {
        method: "POST",
        body: JSON.stringify({
          patient_email: trimmed,
          permissions: {
            view_food_logs: true,
            view_clinical: true,
            view_exercise: true,
            send_nudge: true,
            view_reports: false,
          },
        }),
      });
      toast.success("¡Vínculo familiar establecido con éxito en el servidor!");
      setOpen(false);
      setEmailInput("");
      await refreshAll();
    } catch (err: any) {
      toast.error(err?.message || "No se pudo vincular con el paciente indicado");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" variant="secondary" className="gap-1.5 rounded-full text-xs">
          <Link2 className="size-3.5 text-primary" />
          Vincular
        </Button>
      </DialogTrigger>

      <DialogContent className="max-w-sm rounded-3xl p-6">
        <DialogHeader className="text-left">
          <DialogTitle className="font-display text-lg">
            {mode === "paciente" ? "Comparte con tu familiar" : "Vincular con tu paciente"}
          </DialogTitle>
          <DialogDescription className="text-xs text-muted-foreground">
            {mode === "paciente"
              ? "Tu acompañante verá tu adherencia y te enviará recordatorios cariñosos desde su propio celular."
              : "Introduce el correo del paciente registrado para vincular sus cuentas en la red de cuidado."}
          </DialogDescription>
        </DialogHeader>

        {mode === "paciente" ? (
          <div className="space-y-4 pt-2">
            <div className="rounded-2xl bg-slate-50 p-4 border border-slate-100 text-center space-y-2">
              <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-success-soft text-primary">
                <Users className="size-6" />
              </span>
              <div>
                <p className="text-xs text-muted-foreground">Tu correo para vincular:</p>
                <p className="font-mono text-sm font-bold text-foreground mt-0.5">
                  {profile?.email || "carlos@altoque.pe"}
                </p>
              </div>
            </div>

            <Button
              type="button"
              variant="outline"
              size="sm"
              className="w-full gap-2 rounded-2xl text-xs"
              onClick={() => {
                if (profile?.email) {
                  navigator.clipboard.writeText(profile.email);
                  setCopied(true);
                  toast.success("Correo copiado al portapapeles");
                  setTimeout(() => setCopied(false), 2000);
                }
              }}
            >
              {copied ? <Check className="size-4 text-primary" /> : <Copy className="size-4" />}
              {copied ? "¡Copiado!" : "Copiar mi correo"}
            </Button>
          </div>
        ) : (
          <div className="space-y-4 pt-2">
            <div className="space-y-1.5">
              <Label className="text-xs">Correo del paciente registrado</Label>
              <div className="relative">
                <Input
                  type="email"
                  value={emailInput}
                  onChange={(e) => setEmailInput(e.target.value)}
                  placeholder="paciente@altoque.pe"
                  className="rounded-2xl text-xs pl-8"
                />
                <Mail className="absolute left-2.5 top-2.5 size-3.5 text-muted-foreground" />
              </div>
            </div>
            <Button
              onClick={handlePairCaregiver}
              disabled={busy || !emailInput.trim()}
              className="w-full rounded-2xl bg-primary text-primary-foreground text-xs"
            >
              {busy ? "Vinculando..." : "Confirmar vinculación familiar"}
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
