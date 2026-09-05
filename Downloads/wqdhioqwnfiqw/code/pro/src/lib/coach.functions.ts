import { createServerFn } from "@tanstack/react-start";
import { streamText } from "ai";
import { z } from "zod";

import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";
import { COACH_MODEL, createLovableAiGatewayProvider, requireGatewayKey } from "./ai-gateway.server";

const COACH_SYSTEM = `Eres "Coach Gluco", un coach de salud metabólica peruano, cálido y sin juicios.
Acompañas a personas con prediabetes y a sus familiares.
Principios:
- Nunca prohíbes alimentos ni cuentas calorías. Nada de dietas ni culpa.
- Tu método es: orden del plato (fibra y verduras → proteínas y grasas → carbohidratos), movimiento corto después de comer (esponja muscular), sueño de 6 a 8 horas y manejo del estrés.
- Usas ejemplos de comida peruana real (pollería, chifa, menú, cebiche, lomo saltado, pan con palta).
- Respondes en español, en 3 a 6 frases, cercano, con un emoji como máximo.
- No das diagnósticos ni cambias medicación: si hay síntomas graves, sugieres consultar a su médico.`;

function model() {
  return createLovableAiGatewayProvider(requireGatewayKey())(COACH_MODEL);
}

function gatewayError(error: unknown): never {
  const message = error instanceof Error ? error.message : String(error);
  if (message.includes("402")) throw new Error("Se acabaron los créditos de IA del espacio.");
  if (message.includes("429")) throw new Error("Muchas consultas seguidas. Espera unos segundos.");
  throw new Error(message);
}

const ChatInput = z.object({
  history: z
    .array(z.object({ role: z.enum(["user", "coach"]), content: z.string() }))
    .max(30)
    .default([]),
  message: z.string().min(1).max(1000),
  context: z.string().max(1500).optional(),
});

export const askCoach = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((input: unknown) => ChatInput.parse(input))
  .handler(async ({ data }) => {
    try {
      const result = streamText({
        model: model(),
        system: data.context ? `${COACH_SYSTEM}\n\nContexto de la persona:\n${data.context}` : COACH_SYSTEM,
        messages: [
          ...data.history.map((m) => ({
            role: m.role === "coach" ? ("assistant" as const) : ("user" as const),
            content: m.content,
          })),
          { role: "user" as const, content: data.message },
        ],
      });
      return { text: await result.text };
    } catch (error) {
      gatewayError(error);
    }
  });

const MealInput = z.object({
  meal: z.string().min(2).max(300),
  place: z.enum(["casa", "restaurante"]),
  context: z.string().max(1500).optional(),
});

export type MealPlan = {
  titulo: string;
  pasos: { orden: number; grupo: string; que: string; porque: string }[];
  movimiento: string;
  animo: string;
};

export const planMeal = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((input: unknown) => MealInput.parse(input))
  .handler(async ({ data }): Promise<MealPlan> => {
    const prompt = `La persona va a comer: "${data.meal}" (${data.place === "casa" ? "en casa" : "en un restaurante o menú"}).
${data.context ? `Contexto: ${data.context}` : ""}
Devuelve SOLO un JSON con esta forma exacta:
{"titulo": "resumen corto del plato", "pasos": [{"orden": 1, "grupo": "Fibra y verduras", "que": "qué comer primero de ESE plato", "porque": "razón breve"}], "movimiento": "micro-hábito de movimiento sugerido después de comer", "animo": "frase corta de aliento sin culpa"}
Usa exactamente 3 pasos en este orden de grupos: "Fibra y verduras", "Proteínas y grasas", "Carbohidratos". Habla del plato real que mencionó, sin prohibir nada.`;

    try {
      const result = streamText({ model: model(), system: COACH_SYSTEM, prompt });
      const raw = await result.text;
      const json = raw.slice(raw.indexOf("{"), raw.lastIndexOf("}") + 1);
      const parsed = JSON.parse(json) as MealPlan;
      if (!Array.isArray(parsed.pasos) || parsed.pasos.length === 0) {
        throw new Error("Respuesta incompleta");
      }
      return parsed;
    } catch (error) {
      gatewayError(error);
    }
  });

const RoutineInput = z.object({
  workStart: z.string().default("08:00"),
  workEnd: z.string().default("17:00"),
  wake: z.string().default("06:30"),
  sleep: z.string().default("22:30"),
  notes: z.string().max(600).optional(),
  context: z.string().max(1500).optional(),
});

export type RoutineItem = { hora: string; titulo: string; detalle: string; tipo: string };

export const generateRoutine = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((input: unknown) => RoutineInput.parse(input))
  .handler(async ({ data }): Promise<RoutineItem[]> => {
    const prompt = `Arma una hoja de rutina diaria para una persona con prediabetes.
Se levanta ${data.wake}, trabaja de ${data.workStart} a ${data.workEnd}, se duerme ${data.sleep}.
${data.notes ? `Notas: ${data.notes}` : ""}
${data.context ? `Contexto clínico: ${data.context}` : ""}
Devuelve SOLO un arreglo JSON de entre 8 y 12 objetos, ordenados por hora:
[{"hora":"07:00","titulo":"Desayuno salado","detalle":"qué hacer, concreto y peruano","tipo":"comida"}]
"tipo" solo puede ser: "comida", "movimiento", "descanso", "hidratacion" o "chequeo".
Incluye desayuno salado, caminatas cortas después de cada comida, pausas de hidratación y hora de dormir.`;

    try {
      const result = streamText({ model: model(), system: COACH_SYSTEM, prompt });
      const raw = await result.text;
      const json = raw.slice(raw.indexOf("["), raw.lastIndexOf("]") + 1);
      const parsed = JSON.parse(json) as RoutineItem[];
      if (!Array.isArray(parsed) || parsed.length === 0) throw new Error("Respuesta incompleta");
      return parsed.slice(0, 14);
    } catch (error) {
      gatewayError(error);
    }
  });
