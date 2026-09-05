# GlucoShift: Your Family's Glucose Guide

Create "GlucoShift", a modern, empathetic, mobile-first web app designed to help families and patients reverse prediabetes together through habit adaptation, food sequencing, and daily companionship.

### Tech Stack & Design Aesthetics:

- Tailwind CSS with shadcn/ui components, Lucide icons, and clean card-based layouts.

- Color Palette: Warm, reassuring, medical-tech vibe. Calming emerald/mint green (healthy glucose/success, e.g., #10b981), soft slate/neutral grays (#f8fafc, #1e293b), warm amber for reminders, and gentle coral for glucose alerts.

- Responsive mobile container frame (max-w-md mx-auto min-h-screen bg-slate-50 border-x border-slate-200 shadow-xl) with a persistent bottom navigation bar.

### User Roles & Dual Mode System (Global Switcher):

Include a toggle at the top header or in settings to seamlessly preview the two modes:

1. "Modo Paciente" (Simplified, accessible, larger text, high-contrast, designed for seniors/children).

2. "Modo Acompañante / Cuidador" (Analytical dashboard, progress trackers, nudge buttons).

---

### Core Views & Features to Build:

1. Top Navigation & Pairing Banner:

   - Header with GlucoShift logo, current active profile badge (Paciente vs Familiar), and a quick "Vincular Familiar" button displaying a modal with a QR Code and 6-digit sync PIN.

2. Onboarding & Zero-Typing Medical Ingestion:

   - Quick Upload Card: Drag-and-drop or file upload zone simulation for:

     * "PDF/Foto de Análisis de Sangre" (Mock auto-extraction badge: HbA1c: 5.9%, Glucosa en ayunas: 108 mg/dL).

     * "PDF/Cronograma de Horarios" (Auto-detects work hours 8:00 AM - 5:00 PM and sets meal reminder slots).

3. Smart Plate Sequencer ("¿Qué vas a comer hoy?"):

   - Interactive meal guide showing the scientific anti-spike order:

     1. Fibra & Verduras (Green badge)

     2. Proteínas & Grasas saludables (Blue badge)

     3. Carbohidratos & Almidones (Orange badge)

   - Visual toggle: "En casa" vs "En restaurante / Menú ejecutivo".

     * If "En restaurante", show curated recommendations (e.g., "Pollería: Pide ensalada mixta de entrada, come el pollo y consume solo 1/3 de las papas al final").

   - One-tap confirmation button: "Comí en el orden correcto (+15 pts Curva Plana)".

4. Post-Meal Muscle Activation Tracker ("Esponja Muscular"):

   - Timer card showing: "Han pasado 20 min desde tu almuerzo. Es hora de activar tus músculos".

   - Quick selector for micro-habits: "10 Sentadillas suaves", "Caminata de 5 min" or "Soleus Pushups sentado".

   - Quick checkbox with motivational sound/animation feedback.

5. AI Companion Chatbot ("Coach Gluco"):

   - Floating action button opening an interactive chat drawer.

   - Pre-populated quick chips:

     * "¿Qué pido en un chifa/restaurante chino?"

     * "Estoy en una fiesta y hay torta, ¿cómo la como?"

     * "¿Por qué tengo que dormir entre 6 y 8 horas?"

   - Instant empathetic AI answers focusing on buffering glucose spikes without guilt or caloric restrictions.

6. Cuidador / Familiar Dashboard (Viewable when switching role):

   - Status of linked patient (e.g., "Papá - Nivel de Adherencia Semanal: 88%").

   - Timeline of activities: Breakfast recorded (Order OK), Walk completed, Sleep 7.2h logged.

   - Actionable "Nudge" button: "Enviar recordatorio cariñoso por WhatsApp" with a one-click simulated modal.

   - Weekly meal structural templates: Ideas for family meals that prevent spikes for everyone without cooking separate menus.

7. Mock Data & State Management:

   - Use local state with React hooks to let the judge test:

     * Uploading mock files (triggers a simulated parsing spinner and displays extracted values).

     * Checking off food sequencing and muscle activation.

     * Sending a mock message in the AI chat.

     * Switching between Paciente and Cuidador views.

This project was built with [Lovable](https://lovable.dev).

**Live app**: https://gluco-family-guide.lovable.app

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/5d191f63-bd51-462d-8d22-af08c5709a89).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
