/* Modal de configuración de AlToque AI con URL del backend y preferencias */
import { Globe, LogOut, Server, Shield, Sparkles, User } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAlToque } from "@/lib/altoque-store";
import { guardarUrlApi, obtenerUrlApi } from "@/lib/api-client";

type Props = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function SettingsDialog({ open, onOpenChange }: Props) {
  const { profile, mode, signOut } = useAlToque();
  const [apiUrl, setApiUrl] = useState(obtenerUrlApi());

  const handleSaveUrl = () => {
    guardarUrlApi(apiUrl.trim());
    toast.success("URL de API guardada correctamente");
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm rounded-3xl p-6">
        <DialogHeader>
          <DialogTitle className="font-display text-lg">Configuración</DialogTitle>
          <DialogDescription className="text-xs text-muted-foreground">
            Ajustes del sistema y conexión al backend de AlToque AI.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 pt-2">
          {/* Perfil actual */}
          <div className="flex items-center gap-3 rounded-2xl bg-slate-50 p-3">
            <div className="flex size-10 items-center justify-center rounded-xl bg-success-soft text-lg">
              {profile?.avatar || "🙂"}
            </div>
            <div className="flex-1">
              <p className="text-xs font-semibold text-foreground">
                {profile?.full_name || "Usuario AlToque"}
              </p>
              <p className="text-[11px] text-muted-foreground">
                Modo actual: {mode === "paciente" ? "Paciente" : "Acompañante familiar"}
              </p>
            </div>
            <Badge variant="outline" className="rounded-full bg-white text-[10px] text-primary">
              Activo
            </Badge>
          </div>

          {/* URL del backend API */}
          <div className="space-y-1.5">
            <Label className="text-xs flex items-center gap-1.5">
              <Server className="size-3.5 text-primary" /> Servidor API (FastAPI / Railway)
            </Label>
            <Input
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="http://localhost:8000 o https://tu-backend.railway.app"
              className="rounded-2xl text-xs font-mono"
            />
            <p className="text-[10px] text-muted-foreground">
              Puedes conectar tu despliegue en Railway o el servidor local.
            </p>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleSaveUrl}
              className="flex-1 rounded-2xl bg-primary text-primary-foreground text-xs"
            >
              Guardar cambios
            </Button>
            <Button
              onClick={() => {
                void signOut();
                onOpenChange(false);
              }}
              variant="outline"
              className="rounded-2xl text-xs gap-1 border-rose-200 text-destructive hover:bg-rose-50"
            >
              <LogOut className="size-3.5" /> Salir
            </Button>
          </div>

          <div className="pt-2 text-center text-[10px] text-muted-foreground">
            AlToque AI v1.0.0 · Prevención Metabólica Inteligente
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
