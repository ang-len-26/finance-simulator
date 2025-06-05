import { FC } from "react";
import useFinanceData from "../../hooks/useFinanceData";

const TransactionTable: FC = () => {
  const {
    transactions,
    next,
    previous,
    currentPage,
    totalPages,
    fetchPage,
    filterType,
    setFilterType,
    refreshData,
  } = useFinanceData();

  return (
    <div className="overflow-x-auto rounded-xl shadow bg-white">
      <div className="flex justify-end mb-4">
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value as typeof filterType)}
          className="p-2 border rounded"
        >
          <option value="all">Todos</option>
          <option value="income">Ingreso</option>
          <option value="expense">Gasto</option>
          <option value="investment">Inversión</option>
          <option value="loan">Préstamo</option>
          <option value="savings">Ahorro</option>
        </select>
      </div>
      <table className="min-w-full text-sm text-left">
        <thead>
          <tr className="bg-gray-100 text-gray-700">
            <th className="p-3">Fecha</th>
            <th className="p-3">Título</th>
            <th className="p-3">Tipo</th>
            <th className="p-3">Monto</th>
          </tr>
        </thead>
        <tbody>
          {transactions
            .filter((t) => filterType === "all" || t.type === filterType)
            .map((t) => (
              <tr key={t.id} className="border-t hover:bg-gray-50">
                <td className="p-3">{new Date(t.date).toLocaleDateString()}</td>
                <td className="p-3">{t.title}</td>
                <td className="p-3 capitalize">{t.type}</td>
                <td className="p-3 font-medium text-right">
                  S/. {Number(t.amount).toFixed(2)}
                </td>
              </tr>
            ))}
        </tbody>
      </table>

      {/* Botones de paginación y estado de página */}
      <div className="flex justify-between items-center p-4">
        <button
          onClick={() => previous && fetchPage(previous)}
          disabled={!previous}
          className="bg-gray-200 hover:bg-gray-300 text-sm py-1 px-4 rounded disabled:opacity-50"
        >
          ← Anterior
        </button>

        <span className="text-sm text-gray-600 font-medium">
          Página {currentPage} de {totalPages}
        </span>

        <button
          onClick={() => next && fetchPage(next)}
          disabled={!next}
          className="bg-gray-200 hover:bg-gray-300 text-sm py-1 px-4 rounded disabled:opacity-50"
        >
          Siguiente →
        </button>
      </div>
    </div>
  );
};

export default TransactionTable;
