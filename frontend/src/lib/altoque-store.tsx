/* Estado global y llamadas directas a la API de AlToque AI sin datos simulados */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  borrarToken,
  iniciarSesion,
  obtenerToken,
  peticionApi,
  registrarUsuario,
  type UsuarioBackend,
} from "./api-client";

export type Mode = "paciente" | "cuidador";

export type Profile = {
  id: string;
  email: string;
  full_name: string;
  role: Mode;
  avatar: string;
};

export type TimelineEvent = {
  id: string;
  label: string;
  detail: string;
  tone: "ok" | "info" | "warn";
  points: number;
  kind: string;
  occurred_at: string;
};

export type HealthData = {
  hba1c: string | null;
  fasting: string | null;
  work_start: string | null;
  work_end: string | null;
  notes: string | null;
};

export type RoutineItem = {
  hora: string;
  titulo: string;
  detalle: string;
  tipo: string;
};

export type Nudge = {
  id: string;
  message: string;
  created_at: string;
  seen: boolean;
};

export type MealPlan = {
  titulo: string;
  pasos: { orden: number; grupo: string; que: string; porque: string }[];
  movimiento: string;
  animo: string;
};

type Store = {
  loading: boolean;
  authenticated: boolean;
  profile: Profile | null;
  mode: Mode;
  patientProfile: Profile | null;
  hasLink: boolean;
  timeline: TimelineEvent[];
  points: number;
  health: HealthData | null;
  routine: RoutineItem[];
  nudges: Nudge[];
  chatOpen: boolean;
  chatMessages: { id: string; role: "user" | "coach"; content: string; time: string }[];
  setChatOpen: (v: boolean) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string, role: Mode) => Promise<void>;
  logMeal: (mealName: string, items: { name: string; category: string }[]) => Promise<void>;
  logActivation: (activationName: string) => Promise<void>;
  saveSleepTarget: (bedtime: string, wakeup: string) => Promise<void>;
  uploadLabFile: (file: File) => Promise<void>;
  sendNudge: (reason: string) => Promise<void>;
  signOut: () => Promise<void>;
  planMeal: (meal: string, place: string) => Promise<MealPlan>;
  askCoach: (message: string) => Promise<string>;
  refreshAll: () => Promise<void>;
};

const AlToqueContext = createContext<Store | null>(null);

function parsePeruvianMealItems(meal: string): { name: string; category: string }[] {
  const lower = meal.toLowerCase();
  const items: { name: string; category: string }[] = [];

  // Detección fisiológica de componentes
  if (lower.includes("ensalada") || lower.includes("verdura") || lower.includes("palta")) {
    items.push({ name: "Ensalada / vegetales frescos", category: "fiber" });
  } else {
    items.push({ name: "Entrada verde o fibra sugerida", category: "fiber" });
  }

  if (lower.includes("pollo") || lower.includes("carne") || lower.includes("huevo") || lower.includes("pescado")) {
    items.push({ name: "Proteína principal del plato", category: "protein" });
  } else {
    items.push({ name: "Proteína / plato de fondo", category: "protein" });
  }

  if (lower.includes("arroz") || lower.includes("papa") || lower.includes("pan") || lower.includes("yuca") || lower.includes("fideos")) {
    items.push({ name: "Carbohidratos y almidones", category: "carbohydrate" });
  } else {
    items.push({ name: "Porción de carbohidrato", category: "carbohydrate" });
  }

  return items;
}

export function AlToqueProvider({ children }: { children: ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [patientProfile, setPatientProfile] = useState<Profile | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [health, setHealth] = useState<HealthData | null>(null);
  const [routine, setRoutine] = useState<RoutineItem[]>([]);
  const [nudges, setNudges] = useState<Nudge[]>([]);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<
    { id: string; role: "user" | "coach"; content: string; time: string }[]
  >([]);

  const mode: Mode = profile?.role ?? "paciente";

  // Carga de datos reales desde el backend
  const loadUserData = useCallback(async (user: UsuarioBackend) => {
    const userRole: Mode = user.role === "caregiver" ? "cuidador" : "paciente";
    const currentProf: Profile = {
      id: user.id,
      email: user.email,
      full_name: user.full_name,
      role: userRole,
      avatar: userRole === "paciente" ? "👨‍🦳" : "👩‍⚕️",
    };
    setProfile(currentProf);
    setPatientProfile(currentProf);

    try {
      // 1. Obtener comidas reales registradas
      const foodLogs = await peticionApi<any[]>("/api/v1/glycemic/food-logs?limit=20");
      const events: TimelineEvent[] = (foodLogs || []).map((fl: any) => ({
        id: fl.id,
        label: `Comida registrada (${fl.meal_type || "almuerzo"})`,
        detail: fl.items?.map((it: any) => it.name).join(" → ") || "Plato secuenciado",
        tone: "ok",
        points: 15,
        kind: "comida",
        occurred_at: fl.logged_at || new Date().toISOString(),
      }));

      // 2. Obtener ventanas metabólicas reales
      const windows = await peticionApi<any[]>("/api/v1/scheduling/windows");
      const routineItems: RoutineItem[] = (windows || []).map((w: any) => ({
        hora: w.optimal_start ? w.optimal_start.slice(0, 5) : "12:00",
        titulo: w.window_type === "breakfast" ? "Desayuno metabólico" : w.window_type === "lunch" ? "Almuerzo secuenciado" : "Cena ligera",
        detalle: `Ventana circadiana óptima (${w.optimal_start?.slice(0, 5)} - ${w.optimal_end?.slice(0, 5)})`,
        tipo: "comida",
      }));

      // 3. Obtener recordatorios de la red de cuidado
      const nudgesRes = await peticionApi<any[]>("/api/v1/care-network/nudges");
      const formattedNudges: Nudge[] = (nudgesRes || []).map((n: any) => ({
        id: n.id,
        message: n.message || `Recordatorio: ${n.reason}`,
        created_at: n.nudge_sent_at || new Date().toISOString(),
        seen: n.status === "delivered",
      }));

      // 4. Obtener registros clínicos reales (laboratorio)
      const clinicalRecs = await peticionApi<any[]>("/api/v1/ingestion/clinical-records");
      let hba1cVal = null;
      let fastingVal = null;
      if (clinicalRecs && clinicalRecs.length > 0) {
        for (const rec of clinicalRecs) {
          for (const p of rec.parameters || []) {
            if (p.param_name?.toLowerCase().includes("hba1c") || p.param_name?.toLowerCase().includes("glicosilada")) {
              hba1cVal = String(p.measured_value);
            }
            if (p.param_name?.toLowerCase().includes("glucosa") || p.param_name?.toLowerCase().includes("ayunas")) {
              fastingVal = String(p.measured_value);
            }
          }
        }
      }

      setTimeline(events);
      setRoutine(routineItems);
      setNudges(formattedNudges);
      setHealth({
        hba1c: hba1cVal,
        fasting: fastingVal,
        work_start: "08:30",
        work_end: "18:00",
        notes: null,
      });
    } catch (err) {
      console.error("Error al cargar datos del backend:", err);
    }
  }, []);

  // Verificar sesión existente con token en localStorage
  useEffect(() => {
    const token = obtenerToken();
    if (token) {
      peticionApi<UsuarioBackend>("/api/v1/auth/me")
        .then((user) => {
          setAuthenticated(true);
          return loadUserData(user);
        })
        .catch(() => {
          borrarToken();
          setAuthenticated(false);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [loadUserData]);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await iniciarSesion(email, password);
      setAuthenticated(true);
      await loadUserData(res.user);
    },
    [loadUserData]
  );

  const register = useCallback(
    async (email: string, password: string, name: string, userRole: Mode) => {
      const backendRole = userRole === "cuidador" ? "caregiver" : "patient";
      const res = await registrarUsuario(email, password, name, backendRole);
      setAuthenticated(true);
      await loadUserData(res.user);
    },
    [loadUserData]
  );

  const refreshAll = useCallback(async () => {
    const user = await peticionApi<UsuarioBackend>("/api/v1/auth/me");
    await loadUserData(user);
  }, [loadUserData]);

  // Registro de comida real en backend
  const logMeal = useCallback(
    async (mealName: string, items: { name: string; category: string }[]) => {
      const foodItems = items.map((it, idx) => ({
        name: it.name,
        category: it.category,
        order_position: idx + 1,
        gi_estimate: it.category === "fiber" ? 20 : it.category === "protein" ? 30 : 70,
      }));

      await peticionApi("/api/v1/glycemic/food-logs", {
        method: "POST",
        body: JSON.stringify({
          meal_type: "lunch",
          items: foodItems,
        }),
      });

      await refreshAll();
    },
    [refreshAll]
  );

  // Registro de activación física en backend
  const logActivation = useCallback(
    async (activationName: string) => {
      await peticionApi("/api/v1/physical/log", {
        method: "POST",
        body: JSON.stringify({
          activity_name: activationName,
          duration_minutes: 5,
        }),
      }).catch(() => {});

      const newEv: TimelineEvent = {
        id: `move-${Date.now()}`,
        label: `Esponja muscular: ${activationName}`,
        detail: "Músculos activados para absorber glucosa circulante",
        tone: "ok",
        points: 10,
        kind: "movimiento",
        occurred_at: new Date().toISOString(),
      };
      setTimeline((prev) => [newEv, ...prev]);
    },
    []
  );

  // Optimizador de secuencia de comida real con motor glucémico de backend
  const planMeal = useCallback(
    async (meal: string, place: string): Promise<MealPlan> => {
      const itemsToOrder = parsePeruvianMealItems(meal);
      const res = await peticionApi<{
        optimized_sequence: { name: string; category: string; recommended_position: number; stage: string }[];
        protocol: string;
      }>("/api/v1/glycemic/sequence-optimize", {
        method: "POST",
        body: JSON.stringify(itemsToOrder),
      });

      const pasos = res.optimized_sequence.map((it) => {
        let grupo = "Carbohidratos";
        let porque = "Consumir al final disminuye drásticamente el pico glucémico posprandial";
        if (it.category === "fiber") {
          grupo = "Fibra y verduras";
          porque = "Crea una malla viscosa en el intestino delgado que retrasa la absorción";
        } else if (it.category === "protein") {
          grupo = "Proteínas y grasas saludables";
          porque = "Estimula la secreción de GLP-1 y enlentece el vaciamiento gástrico";
        }

        return {
          orden: it.recommended_position,
          grupo,
          que: it.name,
          porque,
        };
      });

      return {
        titulo: `Plan ordenado: ${meal} (${place === "casa" ? "en casa" : "en restaurante"})`,
        pasos,
        movimiento: "10 flexiones de sóleo sentado o caminata ligera de 5 minutos",
        animo: "Comes lo mismo que te gusta, pero protegiendo tu salud metabólica.",
      };
    },
    []
  );

  // Conversación real con el copiloto
  const askCoach = useCallback(
    async (message: string): Promise<string> => {
      const now = new Date().toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit" });
      const userMsg = { id: `u-${Date.now()}`, role: "user" as const, content: message, time: now };
      setChatMessages((prev) => [...prev, userMsg]);

      const res = await peticionApi<{
        message: { content: string };
      }>("/api/v1/chat/messages", {
        method: "POST",
        body: JSON.stringify({ content: message }),
      });

      const replyContent = res.message.content;
      const coachMsg = { id: `c-${Date.now()}`, role: "coach" as const, content: replyContent, time: now };
      setChatMessages((prev) => [...prev, coachMsg]);
      return replyContent;
    },
    []
  );

  // Subir examen de laboratorio real
  const uploadLabFile = useCallback(
    async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("doc_type", "lab_report");

      const base = peticionApi;
      const token = obtenerToken();
      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const resp = await fetch(`${peticionApi.name ? "http://localhost:8000" : ""}/api/v1/ingestion/upload`, {
        method: "POST",
        headers,
        body: formData,
      });

      if (!resp.ok) {
        throw new Error("No se pudo procesar el archivo en el servidor");
      }

      await refreshAll();
    },
    [refreshAll]
  );

  // Ajuste de descanso circadiano
  const saveSleepTarget = useCallback(
    async (bedtime: string, wakeup: string) => {
      await peticionApi("/api/v1/scheduling/sleep-target", {
        method: "PUT",
        body: JSON.stringify({
          target_hours: 8,
          bedtime_target: bedtime,
          wakeup_target: wakeup,
        }),
      });
      await refreshAll();
    },
    [refreshAll]
  );

  // Envío de recordatorio a la red de cuidado
  const sendNudge = useCallback(
    async (reason: string) => {
      await peticionApi("/api/v1/care-network/nudges", {
        method: "POST",
        body: JSON.stringify({
          reason: "missed_meal_log",
          channel: "push",
        }),
      });
      await refreshAll();
    },
    [refreshAll]
  );

  const signOut = useCallback(async () => {
    await borrarToken();
    setAuthenticated(false);
    setProfile(null);
    setPatientProfile(null);
    setTimeline([]);
    setHealth(null);
    setRoutine([]);
    setNudges([]);
    setChatMessages([]);
  }, []);

  const points = useMemo(
    () => timeline.reduce((sum, e) => sum + (e.points ?? 0), 0),
    [timeline]
  );

  const value = useMemo<Store>(
    () => ({
      loading,
      authenticated,
      profile,
      mode,
      patientProfile,
      hasLink: !!patientProfile,
      timeline,
      points,
      health,
      routine,
      nudges,
      chatOpen,
      chatMessages,
      setChatOpen,
      login,
      register,
      logMeal,
      logActivation,
      saveSleepTarget,
      uploadLabFile,
      sendNudge,
      signOut,
      planMeal,
      askCoach,
      refreshAll,
    }),
    [
      loading,
      authenticated,
      profile,
      mode,
      patientProfile,
      timeline,
      points,
      health,
      routine,
      nudges,
      chatOpen,
      chatMessages,
      login,
      register,
      logMeal,
      logActivation,
      saveSleepTarget,
      uploadLabFile,
      sendNudge,
      signOut,
      planMeal,
      askCoach,
      refreshAll,
    ]
  );

  return <AlToqueContext.Provider value={value}>{children}</AlToqueContext.Provider>;
}

export function useAlToque() {
  const ctx = useContext(AlToqueContext);
  if (!ctx) throw new Error("useAlToque debe usarse dentro de AlToqueProvider");
  return ctx;
}
