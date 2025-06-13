import { FC, useMemo, useState } from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Transaction } from "../../types/Transaction";

ChartJS.register(ArcElement, Tooltip, Legend);

interface Props {
  transactions: Transaction[];
}

const colorMap: Record<string, string> = {
  expense: "#ef4444", // rojo
  loan: "#3b82f6", // azul
  savings: "#facc15", // amarillo
  investment: "#10b981", // verde
};

const TransactionPieChart: FC<Props> = ({ transactions }) => {
  const [selectedMonth, setSelectedMonth] = useState<string>("");

  // Generar lista de meses únicos
  const availableMonths = useMemo(() => {
    const months = new Set<string>();
    transactions.forEach((t) => {
      const date = new Date(t.date);
      const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
        2,
        "0"
      )}`;
      months.add(key);
    });
    return Array.from(months).sort().reverse();
  }, [transactions]);

  // Obtener datos del mes seleccionado
  const monthlyData = useMemo(() => {
    const result: Record<string, number> = {};
    let incomeTotal = 0;

    transactions.forEach((t) => {
      const date = new Date(t.date);
      const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
        2,
        "0"
      )}`;

      if (key === selectedMonth) {
        if (t.type === "income") {
          incomeTotal += Number(t.amount);
        } else {
          if (!result[t.type]) result[t.type] = 0;
          result[t.type] += Number(t.amount);
        }
      }
    });

    return {
      data: result,
      income: incomeTotal,
    };
  }, [transactions, selectedMonth]);

  const labels = Object.keys(monthlyData.data);
  const values = Object.values(monthlyData.data);
  const totalEgresos = values.reduce((a, b) => a + b, 0);

  const chartData = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: labels.map((label) => colorMap[label]),
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow">
      <h2 className="text-lg font-semibold mb-4">
        Proporción de egresos por tipo
      </h2>

      <div className="mb-4">
        <label className="text-sm font-medium mr-2">Selecciona un mes:</label>
        <select
          className="border px-2 py-1 rounded"
          value={selectedMonth}
          onChange={(e) => setSelectedMonth(e.target.value)}
        >
          <option value="">-- Mes --</option>
          {availableMonths.map((m) => (
            <option key={m} value={m}>
              {new Date(m + "-01").toLocaleDateString("es-PE", {
                year: "numeric",
                month: "long",
              })}
            </option>
          ))}
        </select>
      </div>

      {selectedMonth && labels.length > 0 ? (
        <div className="flex flex-col md:flex-row gap-6 items-center">
          <div className="w-full md:w-1/2">
            <ul className="space-y-2">
              {labels.map((label, i) => {
                const value = monthlyData.data[label];
                const percent = ((value / monthlyData.income) * 100).toFixed(1);
                return (
                  <li key={label} className="flex items-center gap-2 text-sm">
                    <span
                      className="w-4 h-4 inline-block rounded"
                      style={{ backgroundColor: colorMap[label] }}
                    />
                    <span className="font-medium capitalize">{label}</span>
                    <span className="ml-auto text-gray-700 font-semibold">
                      {percent}% (S/. {value.toFixed(2)})
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>
          <div className="w-full md:w-1/2 max-w-[300px]">
            <Pie data={chartData} />
          </div>
        </div>
      ) : selectedMonth ? (
        <p className="text-sm text-gray-500">No hay datos para este mes.</p>
      ) : (
        <p className="text-sm text-gray-400">
          Selecciona un mes para ver los datos.
        </p>
      )}

      {selectedMonth && (
        <p className="mt-4 text-sm text-gray-600">
          Ingreso total del mes:{" "}
          <strong className="text-green-600">
            S/. {monthlyData.income.toFixed(2)}
          </strong>
        </p>
      )}
    </div>
  );
};

export default TransactionPieChart;
