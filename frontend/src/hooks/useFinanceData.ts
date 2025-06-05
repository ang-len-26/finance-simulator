import { useFinance } from "../context/FinanceContext";

const useFinanceData = () => {
  const {
    transactions,
    next,
    previous,
    currentPage,
    totalPages,
    fetchPage,
    refreshData,
	filterType,
	setFilterType,
  } = useFinance();

  const income = transactions.filter((t) => t.type === "income");
  const expenses = transactions.filter((t) => t.type === "expense");

  return {
    transactions,
    income,
    expenses,
    next,
    previous,
    currentPage,
    totalPages,
    fetchPage,
    refreshData,
    filterType,
    setFilterType,
  };
};

export default useFinanceData;
