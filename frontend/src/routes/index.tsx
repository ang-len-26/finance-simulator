import { Routes, Route, Navigate } from "react-router-dom";
import Home from "../pages/Home";
import Dashboard from "../pages/Dashboard";
import Login from "../pages/Login";
import { JSX } from "react";
import { FinanceProvider } from "../context/FinanceContext";

const PrivateRoute = ({ children }: { children: JSX.Element }) => {
  const token = sessionStorage.getItem("token");
  return token ? children : <Navigate to="/login" />;
};

const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/login" element={<Login />} />
    <Route
      path="/dashboard"
      element={
        <PrivateRoute>
          <FinanceProvider>
            <Dashboard />
          </FinanceProvider>
        </PrivateRoute>
      }
    />
    {/* Ruta por defecto si no encuentra coincidencias */}
    <Route path="*" element={<Navigate to="/" />} />
  </Routes>
);

export default AppRoutes;
