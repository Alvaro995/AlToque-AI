import { Activity, HeartHandshake, Loader2, User } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { lovable } from "@/integrations/lovable/index";
import { supabase } from "@/integrations/supabase/client";
import { cn } from "@/lib/utils";

type Role = "paciente" | "cuidador";

export function AuthScreen() {
  const [tab, setTab] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState<Role>("paciente");
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      if (tab === "login") {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      } else {
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: window.location.origin,
            data: { full_name: name, role },
          },
        });
        if (error) throw error;
        toast.success("Cuenta creada. ¡Bienvenido a GlucoShift!");
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "No se pudo continuar");
    } finally {
      setBusy(false);
    }
  };

  const google = async () => {
    const result = await lovable.auth.signInWithOAuth("google", {
      redirect_uri: window.location.origin,
    });
    if (result.error) toast.error("No se pudo entrar con Google");
  };

  return (
    <div className="flex min-h-screen flex-col justify-center px-6 py-10">
      <div className="mb-6 text-center">
        <span className="mx-auto flex size-14 items-center justify-center rounded-3xl bg-primary text-primary-foreground">
          <Activity className="size-7" />
        </span>
        <h1 className="font-display mt-3 text-2xl text-foreground">GlucoShift</h1>
        <p className="text-sm text-muted-foreground">
          Entra con tu cuenta para sincronizar los teléfonos de la familia.
        </p>
      </div>

      <div className="mb-4 flex rounded-full bg-slate-200/70 p-1">
        {(
          [
            { key: "login", label: "Iniciar sesión" },
            { key: "signup", label: "Crear cuenta" },
          ] as const
        ).map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => setTab(t.key)}
            className={cn(
              "flex-1 rounded-full py-2 text-sm font-semibold transition-all",
              tab === t.key ? "bg-white text-primary shadow-sm" : "text-muted-foreground",
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      <form onSubmit={submit} className="space-y-3">
        {tab === "signup" && (
          <>
            <div className="space-y-1.5">
              <Label htmlFor="name">¿Cómo te llamas?</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Jorge Ramírez"
                required
                className="rounded-2xl"
              />
            </div>
            <div className="space-y-1.5">
              <Label>¿Quién usará este teléfono?</Label>
              <div className="grid grid-cols-2 gap-2">
                {(
                  [
                    { key: "paciente", label: "Soy el paciente", icon: User },
                    { key: "cuidador", label: "Acompaño a alguien", icon: HeartHandshake },
                  ] as const
                ).map((r) => {
                  const Icon = r.icon;
                  return (
                    <button
                      key={r.key}
                      type="button"
                      onClick={() => setRole(r.key)}
                      className={cn(
                        "rounded-2xl border p-3 text-left text-xs font-semibold transition-all",
                        role === r.key
                          ? "border-primary bg-success-soft text-accent-foreground"
                          : "border-slate-200 bg-white text-muted-foreground",
                      )}
                    >
                      <Icon className="mb-1 size-4" />
                      {r.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </>
        )}
        <div className="space-y-1.5">
          <Label htmlFor="email">Correo</Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="rounded-2xl"
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="password">Contraseña</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            className="rounded-2xl"
          />
        </div>
        <Button type="submit" disabled={busy} className="w-full rounded-full" size="lg">
          {busy && <Loader2 className="size-4 animate-spin" />}
          {tab === "login" ? "Entrar" : "Crear mi cuenta"}
        </Button>
      </form>

      <div className="my-4 flex items-center gap-3 text-xs text-muted-foreground">
        <span className="h-px flex-1 bg-slate-200" /> o <span className="h-px flex-1 bg-slate-200" />
      </div>
      <Button variant="outline" className="w-full rounded-full bg-white" onClick={google}>
        Continuar con Google
      </Button>
    </div>
  );
}
