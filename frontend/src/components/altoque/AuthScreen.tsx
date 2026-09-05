/* Pantalla de autenticación y registro real de AlToque AI */
import { Activity, HeartHandshake, Loader2, User } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAlToque } from "@/lib/altoque-store";
import { cn } from "@/lib/utils";

type Role = "paciente" | "cuidador";

export function AuthScreen() {
  const { login, register } = useAlToque();
  const [tab, setTab] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState<Role>("paciente");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (tab === "login") {
        await login(email, password);
      } else {
        await register(email, password, name, role);
      }
    } catch (err: any) {
      setError(err?.message || "Error de comunicación con el servidor");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col justify-center px-6 py-10">
      <div className="mb-6 text-center">
        <span className="mx-auto flex size-14 items-center justify-center rounded-3xl bg-primary text-primary-foreground shadow-lg shadow-primary/20">
          <Activity className="size-7" />
        </span>
        <h1 className="font-display mt-3 text-2xl font-bold text-foreground">AlToque AI</h1>
        <p className="text-xs text-muted-foreground mt-1">
          Copiloto inteligente de prevención metabólica
        </p>
      </div>

      <div className="mb-4 flex rounded-full bg-slate-200/70 p-1">
        {([
          { key: "login" as const, label: "Iniciar sesión" },
          { key: "signup" as const, label: "Crear cuenta" },
        ]).map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => {
              setTab(t.key);
              setError("");
            }}
            className={cn(
              "flex-1 rounded-full py-2 text-xs font-semibold transition-all",
              tab === t.key ? "bg-white text-primary shadow-sm" : "text-muted-foreground",
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-4 rounded-2xl bg-rose-50 border border-rose-200 p-3 text-xs text-rose-700 font-medium">
          {error}
        </div>
      )}

      <form onSubmit={submit} className="space-y-3.5">
        {tab === "signup" && (
          <>
            <div className="space-y-1">
              <Label htmlFor="name" className="text-xs">Nombre y apellido</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Carlos Mendoza"
                required
                minLength={2}
                className="rounded-2xl text-xs"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Rol en el programa</Label>
              <div className="grid grid-cols-2 gap-2">
                {([
                  { key: "paciente" as const, label: "Soy el paciente", icon: User },
                  { key: "cuidador" as const, label: "Acompañante familiar", icon: HeartHandshake },
                ]).map((r) => {
                  const Icon = r.icon;
                  return (
                    <button
                      key={r.key}
                      type="button"
                      onClick={() => setRole(r.key)}
                      className={cn(
                        "rounded-2xl border p-2.5 text-left text-xs font-semibold transition-all",
                        role === r.key
                          ? "border-primary bg-success-soft text-accent-foreground shadow-xs"
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

        <div className="space-y-1">
          <Label htmlFor="email" className="text-xs">Correo electrónico</Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="usuario@ejemplo.pe"
            required
            className="rounded-2xl text-xs"
          />
        </div>

        <div className="space-y-1">
          <Label htmlFor="password" className="text-xs">Contraseña (mínimo 8 caracteres)</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            minLength={8}
            className="rounded-2xl text-xs"
          />
        </div>

        <Button
          type="submit"
          disabled={busy}
          className="w-full rounded-2xl bg-primary text-primary-foreground shadow-md shadow-primary/25"
          size="lg"
        >
          {busy && <Loader2 className="size-4 animate-spin mr-1.5" />}
          {tab === "login" ? "Iniciar sesión" : "Registrarme"}
        </Button>
      </form>
    </div>
  );
}
