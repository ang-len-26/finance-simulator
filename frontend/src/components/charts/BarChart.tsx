import { FC } from "react";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { Transaction } from "../../types/Transaction";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

interface BarChartProps {
  transactions: Transaction[];
}

const BarChart: FC<BarChartProps> = ({ transactions }) => {
  const monthlyData: { [key: string]: { income: number; expense: number } } =
    {};

  transactions.forEach((t) => {
    const date = new Date(t.date);
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
      2,
      "0"
    )}`;

    if (!monthlyData[key]) {
      monthlyData[key] = { income: 0, expense: 0 };
    }

    if (t.type === "income") {
      monthlyData[key].income += Number(t.amount);
    } else if (t.type === "expense") {
      monthlyData[key].expense += Number(t.amount);
    }
  });

  const labels = Object.keys(monthlyData).sort();
  const incomeData = labels.map((label) => monthlyData[label].income);
  const expenseData = labels.map((label) => monthlyData[label].expense);

  const data = {
    labels,
    datasets: [
      {
        label: "Ingresos",
        data: incomeData,
        backgroundColor: "rgba(34, 197, 94, 0.7)", // verde
      },
      {
        label: "Egresos",
        data: expenseData,
        backgroundColor: "rgba(239, 68, 68, 0.7)", // rojo
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
  };

  return (
    <div className="bg-white p-4 rounded-xl shadow">
      <h2 className="text-lg font-semibold mb-4">
        Ingresos vs Egresos por mes
      </h2>
      <Bar data={data} options={options} />
    </div>
  );
};

export default BarChart;
