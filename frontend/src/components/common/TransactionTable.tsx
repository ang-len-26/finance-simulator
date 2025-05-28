import { FC } from "react";
import useFinanceData from "../../hooks/useFinanceData";

const TransactionTable: FC = () => {
  const { transactions } = useFinanceData();

  return (
    <div className="overflow-x-auto rounded-xl shadow bg-white">
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
          {transactions.map((t) => (
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
    </div>
  );
};

export default TransactionTable;
