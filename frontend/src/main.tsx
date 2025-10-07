import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css"; // ✅ Tailwind
import "./styles/globals.css"; // ✅ Variables CSS
import "./styles/components.css"; // ✅ Componentes
import App from "./App.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
