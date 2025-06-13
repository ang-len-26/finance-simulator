import { FC, useState } from "react";
import useFinanceData from "../../hooks/useFinanceData";
import { Transaction } from "../../types/Transaction";

interface Props {
  transactions: Transaction[];
}

const TransactionTable: FC<Props> = ({ transactions }) => {
  const {
    next,
    previous,
    currentPage,
    totalPages,
    fetchPage,
    filterType,
    setFilterType,
    refreshData,
  } = useFinanceData();
  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState<"date" | "amount" | "">("");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const sortTransactions = (data: Transaction[]) => {
    if (!sortField) return data;

    return [...data].sort((a, b) => {
      const valueA =
        sortField === "date" ? new Date(a.date).getTime() : Number(a.amount);
      const valueB =
        sortField === "date" ? new Date(b.date).getTime() : Number(b.amount);

      return sortOrder === "asc" ? valueA - valueB : valueB - valueA;
    });
  };

  const handleSort = (field: "date" | "amount") => {
    if (sortField === field) {
      // si ya está ordenando por ese campo, cambia el orden
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortOrder("asc");
    }
  };

  return (
    <div className="overflow-x-auto rounded-xl shadow bg-white">
      <div className="flex justify-end mb-4">
        {/* selector tipo */}
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

        {/* campo de búsqueda */}
        <input
          type="text"
          placeholder="Buscar por título o descripción"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="p-2 border rounded w-full sm:w-64"
        />

        {/* ordenamiento */}

        <select
          value={sortField}
          onChange={(e) =>
            setSortField(e.target.value as "date" | "amount" | "")
          }
          className="p-2 border rounded"
        >
          <option value="">Ordenar por</option>
          <option value="date">Fecha</option>
          <option value="amount">Monto</option>
        </select>

        <button
          onClick={() =>
            setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"))
          }
          className="p-2 border rounded bg-gray-100 hover:bg-gray-200"
        >
          {sortOrder === "asc" ? "Ascendente ↑" : "Descendente ↓"}
        </button>
      </div>
      <table className="min-w-full text-sm text-left">
        <thead>
          <tr className="bg-gray-100 text-gray-700">
            <th
              className="p-3 cursor-pointer select-none"
              onClick={() => handleSort("date")}
            >
              Fecha{" "}
              {sortField === "date" && (
                <span
                  className={`font-bold ${
                    sortOrder === "asc" ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {sortOrder === "asc" ? "↑" : "↓"}
                </span>
              )}
            </th>
            <th className="p-3">Título</th>
            <th className="p-3">Tipo</th>
            <th
              className="p-3 cursor-pointer select-none text-right"
              onClick={() => handleSort("amount")}
            >
              Monto{" "}
              {sortField === "amount" && (
                <span
                  className={`font-bold ${
                    sortOrder === "asc" ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {sortOrder === "asc" ? "↑" : "↓"}
                </span>
              )}
            </th>
          </tr>
        </thead>
        <tbody>
          {sortTransactions(
            transactions.filter((t) => {
              const matchesType = filterType === "all" || t.type === filterType;
              const matchesSearch =
                t.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (t.description?.toLowerCase() || "").includes(
                  searchTerm.toLowerCase()
                );

              return matchesType && matchesSearch;
            })
          ).map((t) => (
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
