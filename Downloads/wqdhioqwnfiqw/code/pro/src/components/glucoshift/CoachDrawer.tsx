import { Loader2, Send, Sprout } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { supabase } from "@/integrations/supabase/client";
import { askCoach } from "@/lib/coach.functions";
import { useGlucoShift } from "@/lib/glucoshift-store";
import { cn } from "@/lib/utils";

const CHIPS = [
  "¿Qué pido en un chifa?",
  "Hay torta en una fiesta, ¿cómo la como?",
  "¿Por qué debo dormir de 6 a 8 horas?",
  "Se me antoja pan a media tarde",
];

const WELCOME =
  "Hola, soy Coach Gluco 👋 Estoy aquí para acompañarte, sin dietas ni culpas. Cuéntame qué vas a comer o qué te preocupa hoy.";

type Msg = { id: string; role: "user" | "coach"; content: string };

export function CoachDrawer() {
  const { chatOpen, setChatOpen, user, health, mode, patientProfile } = useGlucoShift();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [draft, setDraft] = useState("");
  const [thinking, setThinking] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!user || !chatOpen) return;
    void supabase
      .from("chat_messages")
      .select("id, role, content")
      .eq("user_id", user.id)
      .order("created_at", { ascending: true })
      .limit(40)
      .then(({ data }) => setMessages((data as Msg[] | null) ?? []));
  }, [user, chatOpen]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinking, chatOpen]);

  const context = [
    mode === "cuidador"
      ? `Quien escribe es el familiar acompañante de ${patientProfile?.full_name || "el paciente"}.`
      : "Quien escribe es la persona con prediabetes.",
    health?.hba1c ? `HbA1c: ${health.hba1c}.` : "",
    health?.fasting ? `Glucosa en ayunas: ${health.fasting}.` : "",
    health?.work_start ? `Trabaja de ${health.work_start} a ${health.work_end}.` : "",
  ]
    .filter(Boolean)
    .join(" ");

  const submit = async (text: string) => {
    const value = text.trim();
    if (!value || thinking || !user) return;
    setDraft("");
    const history = messages.slice(-12).map((m) => ({ role: m.role, content: m.content }));
    setMessages((m) => [...m, { id: `local-${Date.now()}`, role: "user", content: value }]);
    setThinking(true);
    void supabase.from("chat_messages").insert({ user_id: user.id, role: "user", content: value });
    try {
      const res = await askCoach({ data: { history, message: value, context } });
      setMessages((m) => [...m, { id: `local-${Date.now()}-c`, role: "coach", content: res.text }]);
      void supabase
        .from("chat_messages")
        .insert({ user_id: user.id, role: "coach", content: res.text });
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "El coach no pudo responder");
    } finally {
      setThinking(false);
    }
  };

  const shown = messages.length
    ? messages
    : [{ id: "welcome", role: "coach" as const, content: WELCOME }];

  return (
    <Sheet open={chatOpen} onOpenChange={setChatOpen}>
      <SheetContent
        side="bottom"
        className="mx-auto flex h-[85vh] max-w-md flex-col rounded-t-3xl bg-slate-50 p-0"
      >
        <SheetHeader className="border-b border-slate-200 bg-white px-4 py-3">
          <SheetTitle className="flex items-center gap-2 text-left">
            <span className="flex size-9 items-center justify-center rounded-2xl bg-success-soft text-primary">
              <Sprout className="size-5" />
            </span>
            <span>
              <span className="font-display block text-base">Coach Gluco</span>
              <span className="block text-xs font-normal text-muted-foreground">
                Con IA · sin dietas, sin culpa
              </span>
            </span>
          </SheetTitle>
        </SheetHeader>

        <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
          {shown.map((m) => (
            <div
              key={m.id}
              className={cn(
                "max-w-[85%] text-sm leading-relaxed whitespace-pre-wrap",
                m.role === "user"
                  ? "ml-auto rounded-2xl rounded-br-sm bg-primary px-4 py-2.5 text-primary-foreground"
                  : "mr-auto rounded-2xl rounded-bl-sm bg-white px-4 py-2.5 text-card-foreground shadow-sm ring-1 ring-slate-200",
              )}
            >
              {m.content}
            </div>
          ))}
          {thinking && (
            <div className="mr-auto flex items-center gap-2 rounded-2xl rounded-bl-sm bg-white px-4 py-2.5 text-sm text-muted-foreground shadow-sm ring-1 ring-slate-200">
              <Loader2 className="size-4 animate-spin" /> Pensando contigo...
            </div>
          )}
          <div ref={endRef} />
        </div>

        <div className="border-t border-slate-200 bg-white px-4 pt-3 pb-5">
          <div className="mb-3 flex gap-2 overflow-x-auto pb-1">
            {CHIPS.map((chip) => (
              <button
                key={chip}
                type="button"
                onClick={() => void submit(chip)}
                className="shrink-0 rounded-full bg-success-soft px-3 py-1.5 text-xs font-medium text-accent-foreground"
              >
                {chip}
              </button>
            ))}
          </div>
          <form
            className="flex items-center gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              void submit(draft);
            }}
          >
            <Input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Escríbele a tu coach..."
              className="rounded-full bg-slate-100"
            />
            <Button
              type="submit"
              size="icon"
              disabled={thinking}
              className="size-10 shrink-0 rounded-full"
            >
              {thinking ? <Loader2 className="size-4 animate-spin" /> : <Send className="size-4" />}
            </Button>
          </form>
        </div>
      </SheetContent>
    </Sheet>
  );
}
