import { FC, useMemo } from "react";
import useFinanceData from "../../hooks/useFinanceData";
import { Transaction } from "../../types/Transaction";

interface Props {
  transactions: Transaction[];
}

const TransactionSummary: FC<Props> = ({ transactions }) => {
  const { filterType } = useFinanceData();

  const summary = useMemo(() => {
    const totals = {
      income: 0,
      expense: 0,
      investment: 0,
      loan: 0,
      savings: 0,
      total: 0,
    };

    transactions.forEach((t) => {
      const amount = Number(t.amount);
      totals[t.type] += amount;
      totals.total += amount;
    });

    return totals;
  }, [transactions]);

  const boxStyle = (type: string) =>
    filterType !== "all" && filterType !== type
      ? "opacity-40 blur-[1px]"
      : "opacity-100";

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4 my-6">
      <div
        className={`bg-green-100 p-3 rounded shadow text-center ${boxStyle(
          "income"
        )}`}
      >
        <p className="text-sm text-green-800 font-medium">Ingresos</p>
        <p className="text-lg font-bold">S/. {summary.income.toFixed(2)}</p>
      </div>
      <div
        className={`bg-red-100 p-3 rounded shadow text-center ${boxStyle(
          "expense"
        )}`}
      >
        <p className="text-sm text-red-800 font-medium">Gastos</p>
        <p className="text-lg font-bold">S/. {summary.expense.toFixed(2)}</p>
      </div>
      <div
        className={`bg-blue-100 p-3 rounded shadow text-center ${boxStyle(
          "investment"
        )}`}
      >
        <p className="text-sm text-blue-800 font-medium">Inversión</p>
        <p className="text-lg font-bold">S/. {summary.investment.toFixed(2)}</p>
      </div>
      <div
        className={`bg-yellow-100 p-3 rounded shadow text-center ${boxStyle(
          "loan"
        )}`}
      >
        <p className="text-sm text-yellow-800 font-medium">Préstamos</p>
        <p className="text-lg font-bold">S/. {summary.loan.toFixed(2)}</p>
      </div>
      <div
        className={`bg-purple-100 p-3 rounded shadow text-center ${boxStyle(
          "savings"
        )}`}
      >
        <p className="text-sm text-purple-800 font-medium">Ahorros</p>
        <p className="text-lg font-bold">S/. {summary.savings.toFixed(2)}</p>
      </div>
      <div className="bg-gray-200 p-3 rounded shadow text-center">
        <p className="text-sm text-gray-800 font-medium">Total</p>
        <p className="text-lg font-bold">S/. {summary.total.toFixed(2)}</p>
      </div>
    </div>
  );
};

export default TransactionSummary;
