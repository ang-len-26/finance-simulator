import TransactionTable from "../common/TransactionTable";
import SpendingChart from "../charts/SpendingChart";
import { useAuth } from "../../context/AuthContext";

const DashboardSection = () => {
  const { username, logout } = useAuth();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
      <h2 className="text-xl font-semibold col-span-2">
        Bienvenido, {username}
      </h2>
      <div className="col-span-2">
        <h3 className="text-lg font-semibold">Resumen de Gastos</h3>
        <p className="text-gray-600">
          Aquí puedes ver un resumen de tus gastos.
        </p>
      </div>
      <div className="col-span-2">
        <h3 className="text-lg font-semibold">Últimas Transacciones</h3>
        <TransactionTable />
      </div>
      <div className="col-span-2">
        <h3 className="text-lg font-semibold">Gráfico de Gastos</h3>
        <SpendingChart />
      </div>
      <button onClick={logout}>Cerrar sesión</button>
    </div>
  );
};

export default DashboardSection;
