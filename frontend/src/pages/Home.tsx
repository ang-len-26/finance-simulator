import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();

  const handleLoginRedirect = () => {
    navigate("/login");
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4 bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md text-center max-w-md w-full">
        <h1 className="text-2xl font-bold mb-4">
          Simulador de Finanzas Personales
        </h1>
        <p className="mb-6 text-gray-600">
          Gestiona tus ingresos y gastos con facilidad.
        </p>
        <button
          onClick={handleLoginRedirect}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
        >
          Iniciar sesión
        </button>
      </div>
    </main>
  );
};

export default Home;
