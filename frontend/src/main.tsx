/* Punto de entrada de la aplicación React de AlToque AI */
import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import { AlToqueProvider } from "./lib/altoque-store";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AlToqueProvider>
      <App />
    </AlToqueProvider>
  </React.StrictMode>,
);
