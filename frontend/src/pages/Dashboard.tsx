import React, { useEffect, useRef, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import TransactionTable from "../components/common/TransactionTable";
import TransactionSummary from "../components/common/TransactionSummary";
import useFinanceData from "../hooks/useFinanceData";
import BarChart from "../components/charts/BarChart";
import LineChartView from "../components/charts/LineChart";
import TransactionPieChart from "../components/charts/TransactionPieChart";
import TransactionForm from "../components/common/TransactionForm";
import { Transaction } from "../types/Transaction";

const Dashboard: React.FC = () => {
  const { username, logout } = useAuth();
  const navigate = useNavigate();
  const { transactions } = useFinanceData();

  const [showModal, setShowModal] = useState(false);
  const [localTransactions, setLocalTransactions] =
    useState<Transaction[]>(transactions);
  const modalRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const toggleModal = () => {
    setShowModal((prev) => !prev);
  };

  const handleCreateTransaction = (newTx: Transaction) => {
    setLocalTransactions((prev) => [newTx, ...prev]);
  };
  // Actualizar transacciones locales al recibir nuevas del contexto
  useEffect(() => {
    setLocalTransactions(transactions);
  }, [transactions]);

  // Cerrar con ESC
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setShowModal(false);
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Cerrar al hacer clic fuera del modal
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        setShowModal(false);
      }
    };
    if (showModal) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showModal]);

  return (
    <div className="min-h-screen bg-gray-100 p-8 relative">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Bienvenido, {username}</h1>
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition"
        >
          Cerrar sesión
        </button>
      </div>

      {/* Título y botón */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Transacciones recientes</h2>
        <button
          onClick={toggleModal}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
        >
          Nueva transacción
        </button>
      </div>

      <div className="bg-white rounded shadow p-6">
        <p className="text-gray-600 mb-4">
          Aquí puedes ver un resumen de tus transacciones recientes.
        </p>
        <TransactionSummary transactions={localTransactions} />
        <TransactionTable transactions={localTransactions} />
        <BarChart transactions={localTransactions} />
        <TransactionPieChart transactions={localTransactions} />
        <LineChartView transactions={localTransactions} />
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 animate-fade-in">
          <div
            ref={modalRef}
            className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md transform transition-all duration-300 animate-slide-up relative"
          >
            <button
              className="absolute top-2 right-2 text-gray-500 hover:text-gray-700 text-xl"
              onClick={toggleModal}
              aria-label="Cerrar"
            >
              ✕
            </button>
            <TransactionForm
              onSuccess={toggleModal}
              onCreate={handleCreateTransaction}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
