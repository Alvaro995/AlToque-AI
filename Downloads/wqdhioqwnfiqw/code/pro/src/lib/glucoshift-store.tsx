import type { Session, User } from "@supabase/supabase-js";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { supabase } from "@/integrations/supabase/client";

export type Mode = "paciente" | "cuidador";

export type Profile = {
  id: string;
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

export type RoutineItem = { hora: string; titulo: string; detalle: string; tipo: string };

export type Nudge = { id: string; message: string; created_at: string; seen: boolean };

type Store = {
  loading: boolean;
  session: Session | null;
  user: User | null;
  profile: Profile | null;
  mode: Mode;
  /** Patient whose data is being shown (self for patients, linked patient for caregivers). */
  patientId: string | null;
  patientProfile: Profile | null;
  hasLink: boolean;
  timeline: TimelineEvent[];
  points: number;
  health: HealthData | null;
  routine: RoutineItem[];
  nudges: Nudge[];
  chatOpen: boolean;
  setChatOpen: (v: boolean) => void;
  logEvent: (e: {
    label: string;
    detail?: string;
    tone?: TimelineEvent["tone"];
    points?: number;
    kind?: string;
  }) => Promise<void>;
  saveHealth: (v: Partial<HealthData>) => Promise<void>;
  saveRoutine: (items: RoutineItem[]) => Promise<void>;
  sendNudge: (message: string) => Promise<void>;
  refresh: () => Promise<void>;
  signOut: () => Promise<void>;
};

const GlucoShiftContext = createContext<Store | null>(null);

export function GlucoShiftProvider({ children }: { children: ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [patientProfile, setPatientProfile] = useState<Profile | null>(null);
  const [patientId, setPatientId] = useState<string | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [health, setHealth] = useState<HealthData | null>(null);
  const [routine, setRoutine] = useState<RoutineItem[]>([]);
  const [nudges, setNudges] = useState<Nudge[]>([]);
  const [chatOpen, setChatOpen] = useState(false);

  const user = session?.user ?? null;
  const mode: Mode = profile?.role ?? "paciente";

  useEffect(() => {
    const { data: sub } = supabase.auth.onAuthStateChange((_e, s) => {
      setSession(s);
      if (!s) {
        setProfile(null);
        setPatientProfile(null);
        setPatientId(null);
        setTimeline([]);
        setHealth(null);
        setRoutine([]);
        setNudges([]);
      }
    });
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setLoading(false);
    });
    return () => sub.subscription.unsubscribe();
  }, []);

  const loadAll = useCallback(async () => {
    if (!user) return;
    const { data: me } = await supabase
      .from("profiles")
      .select("id, full_name, role, avatar")
      .eq("id", user.id)
      .maybeSingle();
    const meta = (user.user_metadata ?? {}) as Record<string, unknown>;
    const myProfile = (me as Profile | null) ?? {
      id: user.id,
      full_name: (meta["full_name"] as string) ?? "",
      role: ((meta["role"] as Mode) ?? "paciente") as Mode,
      avatar: "🙂",
    };
    setProfile(myProfile);

    let scoped = user.id;
    if (myProfile.role === "cuidador") {
      const { data: link } = await supabase
        .from("care_links")
        .select("patient_id")
        .eq("caregiver_id", user.id)
        .order("created_at", { ascending: true })
        .limit(1)
        .maybeSingle();
      if (!link) {
        setPatientId(null);
        setPatientProfile(null);
        setTimeline([]);
        setHealth(null);
        setRoutine([]);
        return;
      }
      scoped = link.patient_id;
      const { data: pp } = await supabase
        .from("profiles")
        .select("id, full_name, role, avatar")
        .eq("id", scoped)
        .maybeSingle();
      setPatientProfile((pp as Profile | null) ?? null);
    } else {
      setPatientProfile(myProfile);
    }
    setPatientId(scoped);

    const [ev, hp, rt, nd] = await Promise.all([
      supabase
        .from("events")
        .select("id, label, detail, tone, points, kind, occurred_at")
        .eq("patient_id", scoped)
        .order("occurred_at", { ascending: false })
        .limit(50),
      supabase
        .from("health_profiles")
        .select("hba1c, fasting, work_start, work_end, notes")
        .eq("user_id", scoped)
        .maybeSingle(),
      supabase.from("routines").select("items").eq("user_id", scoped).maybeSingle(),
      supabase
        .from("nudges")
        .select("id, message, created_at, seen")
        .eq("patient_id", scoped)
        .order("created_at", { ascending: false })
        .limit(10),
    ]);
    setTimeline((ev.data as TimelineEvent[] | null) ?? []);
    setHealth((hp.data as HealthData | null) ?? null);
    setRoutine(((rt.data?.items as RoutineItem[] | undefined) ?? []) as RoutineItem[]);
    setNudges((nd.data as Nudge[] | null) ?? []);
  }, [user]);

  useEffect(() => {
    if (user) void loadAll();
  }, [user, loadAll]);

  // Live sync between the two phones.
  useEffect(() => {
    if (!patientId) return;
    const channel = supabase
      .channel(`gluco-${patientId}`)
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "events", filter: `patient_id=eq.${patientId}` },
        () => void loadAll(),
      )
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "nudges", filter: `patient_id=eq.${patientId}` },
        () => void loadAll(),
      )
      .subscribe();
    return () => {
      void supabase.removeChannel(channel);
    };
  }, [patientId, loadAll]);

  // A caregiver waiting to be linked should notice the moment it happens.
  useEffect(() => {
    if (!user || mode !== "cuidador" || patientId) return;
    const channel = supabase
      .channel(`links-${user.id}`)
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "care_links",
          filter: `caregiver_id=eq.${user.id}`,
        },
        () => void loadAll(),
      )
      .subscribe();
    return () => {
      void supabase.removeChannel(channel);
    };
  }, [user, mode, patientId, loadAll]);

  const logEvent = useCallback<Store["logEvent"]>(
    async (e) => {
      if (!user || mode !== "paciente") return;
      await supabase.from("events").insert({
        patient_id: user.id,
        label: e.label,
        detail: e.detail ?? "",
        tone: e.tone ?? "ok",
        points: e.points ?? 0,
        kind: e.kind ?? "otro",
      });
      await loadAll();
    },
    [user, mode, loadAll],
  );

  const saveHealth = useCallback<Store["saveHealth"]>(
    async (v) => {
      if (!user) return;
      await supabase
        .from("health_profiles")
        .upsert({ user_id: user.id, ...v, updated_at: new Date().toISOString() });
      await loadAll();
    },
    [user, loadAll],
  );

  const saveRoutine = useCallback<Store["saveRoutine"]>(
    async (items) => {
      if (!user) return;
      setRoutine(items);
      await supabase
        .from("routines")
        .upsert({ user_id: user.id, items, updated_at: new Date().toISOString() });
    },
    [user],
  );

  const sendNudge = useCallback<Store["sendNudge"]>(
    async (message) => {
      if (!user || !patientId) return;
      await supabase.from("nudges").insert({
        patient_id: patientId,
        sender_id: user.id,
        message,
      });
    },
    [user, patientId],
  );

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
  }, []);

  const points = useMemo(() => timeline.reduce((sum, e) => sum + (e.points ?? 0), 0), [timeline]);

  const value = useMemo<Store>(
    () => ({
      loading,
      session,
      user,
      profile,
      mode,
      patientId,
      patientProfile,
      hasLink: !!patientId && (mode === "paciente" || !!patientProfile),
      timeline,
      points,
      health,
      routine,
      nudges,
      chatOpen,
      setChatOpen,
      logEvent,
      saveHealth,
      saveRoutine,
      sendNudge,
      refresh: loadAll,
      signOut,
    }),
    [
      loading,
      session,
      user,
      profile,
      mode,
      patientId,
      patientProfile,
      timeline,
      points,
      health,
      routine,
      nudges,
      chatOpen,
      logEvent,
      saveHealth,
      saveRoutine,
      sendNudge,
      loadAll,
      signOut,
    ],
  );

  return <GlucoShiftContext.Provider value={value}>{children}</GlucoShiftContext.Provider>;
}

export function useGlucoShift() {
  const ctx = useContext(GlucoShiftContext);
  if (!ctx) throw new Error("useGlucoShift must be used inside GlucoShiftProvider");
  return ctx;
}
