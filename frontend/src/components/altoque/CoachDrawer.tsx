/* Drawer del copiloto conversacional */
import { Loader2, Send, Sprout } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAlToque } from "@/lib/altoque-store";
import { cn } from "@/lib/utils";

const CHIPS = [
  "¿Cómo secuencio mi almuerzo?",
  "¿Qué ejercicio hago después de comer?",
  "¿Por qué importa el orden del plato?",
  "Tengo antojo de algo dulce",
];

const WELCOME =
  "Hola, soy tu copiloto AlToque AI. Estoy aquí para acompañarte en tu prevención metabólica. ¿En qué puedo orientarte hoy?";

type Msg = { id: string; role: "user" | "coach"; content: string };

export function CoachDrawer() {
  const { chatOpen, setChatOpen, askCoach } = useAlToque();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [draft, setDraft] = useState("");
  const [thinking, setThinking] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinking, chatOpen]);

  const submit = async (text: string) => {
    const value = text.trim();
    if (!value || thinking) return;
    setDraft("");
    setMessages((m) => [...m, { id: `u-${Date.now()}`, role: "user", content: value }]);
    setThinking(true);
    try {
      const resp = await askCoach(value);
      setMessages((m) => [...m, { id: `c-${Date.now()}`, role: "coach", content: resp }]);
    } finally {
      setThinking(false);
    }
  };

  const shown = messages.length
    ? messages
    : [{ id: "welcome", role: "coach" as const, content: WELCOME }];

  if (!chatOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center">
      <div className="absolute inset-0 bg-black/40" onClick={() => setChatOpen(false)} />
      <div className="relative mx-auto flex h-[85vh] w-full max-w-md flex-col rounded-t-3xl bg-slate-50">
        <div className="border-b border-slate-200 bg-white px-4 py-3 rounded-t-3xl">
          <div className="flex items-center gap-2">
            <span className="flex size-9 items-center justify-center rounded-2xl bg-success-soft text-primary">
              <Sprout className="size-5" />
            </span>
            <span>
              <span className="font-display block text-base font-semibold">Copiloto AlToque</span>
              <span className="block text-xs font-normal text-muted-foreground">
                Con IA · Guías clínicas ADA/IDF
              </span>
            </span>
            <button
              onClick={() => setChatOpen(false)}
              className="ml-auto text-xl text-muted-foreground"
            >
              &times;
            </button>
          </div>
        </div>

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
              <Loader2 className="size-4 animate-spin" /> Analizando tu consulta...
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
              placeholder="Consulta sobre alimentación, actividad o descanso..."
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
      </div>
    </div>
  );
}
