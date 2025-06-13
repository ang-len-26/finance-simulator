import { FC, useMemo, useState } from "react";
import { PeriodType } from "../../utils/finance";
import { Line } from "react-chartjs-2";
import { useFinance } from "../../context/FinanceContext";
import { Transaction } from "../../types/Transaction";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";

// Registrar los elementos necesarios
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
);

interface Props {
  transactions: Transaction[];
}

const LineChartView: FC<Props> = ({ transactions }) => {
  const { getAggregatedData } = useFinance();
  const [selectedPeriod, setSelectedPeriod] = useState<PeriodType>(
    PeriodType.Monthly
  );

  // Obtenemos los datos mensuales agregados
  const chartData = useMemo(() => {
    return getAggregatedData(selectedPeriod);
  }, [getAggregatedData, selectedPeriod]);

  const labels = chartData.map((d) => d.period);
  const incomes = chartData.map((d) => d.income);
  const expenses = chartData.map((d) => d.expense);
  const balances = chartData.map((d) => d.balance);

  const getTitle = () => {
    switch (selectedPeriod) {
      case "monthly":
        return "Evolución mensual";
      case "quarterly":
        return "Evolución trimestral";
      case "yearly":
        return "Evolución anual";
      default:
        return "Evolución";
    }
  };

  const data = {
    labels,
    datasets: [
      {
        label: "Ingresos",
        data: incomes,
        borderColor: "rgb(34 197 94)", // verde
        backgroundColor: "rgba(34, 197, 94, 0.2)",
        tension: 0.3,
      },
      {
        label: "Gastos",
        data: expenses,
        borderColor: "rgb(239 68 68)", // rojo
        backgroundColor: "rgba(239, 68, 68, 0.2)",
        tension: 0.3,
      },
      {
        label: "Saldo",
        data: balances,
        borderColor: "rgb(59 130 246)", // azul
        backgroundColor: "rgba(59, 130, 246, 0.2)",
        tension: 0.3,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow">
      <h2 className="text-lg font-semibold mb-4 text-gray-700">
        {getTitle()}: Ingresos, Gastos y Saldo
      </h2>
      <select
        value={selectedPeriod}
        onChange={(e) => setSelectedPeriod(e.target.value as PeriodType)}
        className="mb-4 p-2 rounded border border-gray-300"
      >
        <option value={PeriodType.Monthly}>Mensual</option>
        <option value={PeriodType.Quarterly}>Trimestral</option>
        <option value={PeriodType.Yearly}>Anual</option>
      </select>
      <Line data={data} options={options} />
    </div>
  );
};

export default LineChartView;
