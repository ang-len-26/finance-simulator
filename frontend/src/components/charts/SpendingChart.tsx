import { FC } from "react";
import { Pie } from "react-chartjs-2";
import useFinanceData from "../../hooks/useFinanceData";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

const SpendingChart: FC = () => {
  const { expenses } = useFinanceData();

  const dateTotals = expenses.reduce((acc: Record<string, number>, t) => {
    acc[t.date] = (acc[t.date] || 0) + Number(t.amount);
    return acc;
  }, {});

  const data = {
    labels: Object.keys(dateTotals),
    datasets: [
      {
        data: Object.values(dateTotals),
        backgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#8AFFC1",
          "#FF9A8B",
          "#B47AEA",
        ],
      },
    ],
  };

  return (
    <div className="bg-white rounded-xl p-4 shadow">
      <h2 className="text-lg font-semibold mb-2">Gastos por categoría</h2>
      <Pie data={data} />
    </div>
  );
};

export default SpendingChart;
