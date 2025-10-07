import { createBrowserRouter } from "react-router-dom";
import LandingPage from "./pages/Landing/LandingPage";
// Importarás más páginas después:
// import LoginPage from './pages/Auth/LoginPage';
// import Dashboard from './pages/Dashboard/Dashboard';

export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage />,
  },
  // Aquí irán las demás rutas:
  // { path: '/login', element: <LoginPage /> },
  // { path: '/register', element: <RegisterPage /> },
  // { path: '/dashboard', element: <Dashboard /> },
  // etc...
]);
