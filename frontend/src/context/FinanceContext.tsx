import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import apiClient from "../services/apiClient";

interface Transaction {
  id: number;
  date: string;
  title: string;
  amount: string; // porque en tu API es un string ("500.00")
  type: "income" | "expense" | "investment" | "loan" | "savings"; // añade todos los tipos posibles
}

interface FinanceContextType {
  transactions: Transaction[];
  refreshData: () => void;
}

const FinanceContext = createContext<FinanceContextType | undefined>(undefined);

export const FinanceProvider = ({ children }: { children: ReactNode }) => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  const fetchTransactions = async () => {
    try {
      const response = await apiClient.get("/transactions/");
      const results = response.data.results || []; // usa `results` por paginación
      setTransactions(results);
    } catch (err) {
      console.error("Error fetching transactions:", err);
      setTransactions([]);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  return (
    <FinanceContext.Provider
      value={{ transactions, refreshData: fetchTransactions }}
    >
      {children}
    </FinanceContext.Provider>
  );
};

export const useFinance = () => {
  const context = useContext(FinanceContext);
  if (!context) {
    throw new Error("useFinance must be used within a FinanceProvider");
  }
  return context;
};
