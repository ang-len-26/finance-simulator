import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { fetchTransactions } from "../services/transactionService";
import { Transaction } from "../types/Transaction";

interface FinanceContextType {
  transactions: Transaction[];
  next: string | null;
  previous: string | null;
  currentPage: number;
  totalPages: number;
  fetchPage: (url?: string) => void;
  refreshData: () => void;
  filterType: Transaction["type"] | "all";
  setFilterType: (type: Transaction["type"] | "all") => void;
}

const FinanceContext = createContext<FinanceContextType | undefined>(undefined);

export const FinanceProvider = ({ children }: { children: ReactNode }) => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [next, setNext] = useState<string | null>(null);
  const [previous, setPrevious] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filterType, setFilterType] = useState<Transaction["type"] | "all">(
    "all"
  );

  const getPageFromURL = (url: string | null): number | null => {
    if (!url) return null;
    const match = url.match(/page=(\d+)/);
    return match ? parseInt(match[1], 10) : null;
  };

  const loadData = async (url?: string) => {
    try {
      const data = await fetchTransactions();
      setTransactions(data.results);
      setNext(data.next);
      setPrevious(data.previous);

      const pageSize = data.results.length;
      const totalItems = data.count;
      const pageFromURL =
        url && getPageFromURL(url)
          ? getPageFromURL(url)!
          : data.previous
          ? getPageFromURL(data.previous)! + 1
          : 1;

      setCurrentPage(pageFromURL);
      setTotalPages(Math.ceil(totalItems / pageSize));
    } catch (error) {
      console.error("Error loading transactions:", error);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <FinanceContext.Provider
      value={{
        transactions,
        next,
        previous,
        currentPage,
        totalPages,
        fetchPage: loadData,
        refreshData: () => loadData(),
        filterType,
        setFilterType,
      }}
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
