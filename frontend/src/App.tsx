/* Componente raíz de la aplicación AlToque AI */
import { useState } from "react";
import { Toaster } from "sonner";
import { AppShell } from "@/components/altoque/AppShell";
import { TodayView } from "@/components/altoque/TodayView";
import { HealthView } from "@/components/altoque/HealthView";
import { FamilyView } from "@/components/altoque/FamilyView";
import { SettingsDialog } from "@/components/altoque/SettingsDialog";

export function App() {
  const [currentTab, setCurrentTab] = useState<string>("hoy");
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <>
      <AppShell
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        onSettingsOpen={() => setSettingsOpen(true)}
      >
        {currentTab === "hoy" && <TodayView />}
        {currentTab === "salud" && <HealthView />}
        {currentTab === "familia" && <FamilyView />}
      </AppShell>

      <SettingsDialog
        open={settingsOpen}
        onOpenChange={setSettingsOpen}
      />

      <Toaster position="top-center" richColors />
    </>
  );
}

export default App;
