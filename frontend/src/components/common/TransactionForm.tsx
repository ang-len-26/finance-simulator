import { FC, useState } from "react";
import { useFinance } from "../../context/FinanceContext";
import { createTransaction } from "../../services/transactionService";
import { Transaction } from "../../types/Transaction";

interface TransactionFormProps {
  onSuccess?: () => void; // Puede cerrar modal o recargar datos extra
  onCreate?: (transaction: Transaction) => void;
}

const TransactionForm: FC<TransactionFormProps> = ({ onSuccess, onCreate }) => {
  const { refreshData } = useFinance();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    title: "",
    amount: "",
    type: "income",
    date: "",
    description: "",
  });

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const newTransaction = await createTransaction({
        title: form.title,
        amount: parseFloat(form.amount),
        type: form.type as Transaction["type"],
        date: form.date,
        description: form.description,
      });

      setForm({
        title: "",
        amount: "",
        type: "income",
        date: "",
        description: "",
      });

      if (onCreate) onCreate(newTransaction);
      if (refreshData) refreshData(); // recarga datos visibles
      if (onSuccess) onSuccess(); // puede cerrar el modal si aplica
    } catch (err) {
      setError("Hubo un error al crear la transacción.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-6 rounded-xl shadow mb-6 space-y-4"
    >
      <h2 className="text-lg font-semibold text-gray-700">Nueva Transacción</h2>

      {error && <p className="text-red-600">{error}</p>}

      <input
        type="text"
        name="title"
        value={form.title}
        onChange={handleChange}
        placeholder="Título"
        required
        className="w-full border border-gray-300 rounded p-2"
      />

      <input
        type="number"
        name="amount"
        value={form.amount}
        onChange={handleChange}
        placeholder="Monto"
        required
        className="w-full border border-gray-300 rounded p-2"
        step="0.01"
      />

      <select
        name="type"
        value={form.type}
        onChange={handleChange}
        className="w-full border border-gray-300 rounded p-2"
      >
        <option value="income">Ingreso</option>
        <option value="expense">Gasto</option>
        <option value="investment">Inversión</option>
        <option value="loan">Préstamo</option>
        <option value="savings">Ahorro</option>
      </select>

      <input
        type="date"
        name="date"
        value={form.date}
        onChange={handleChange}
        required
        className="w-full border border-gray-300 rounded p-2"
      />

      <textarea
        name="description"
        value={form.description}
        onChange={handleChange}
        placeholder="Descripción"
        className="w-full border border-gray-300 rounded p-2"
      />

      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        {loading ? "Guardando..." : "Crear"}
      </button>
    </form>
  );
};

export default TransactionForm;
