import { useFinance } from '../context/FinanceContext';

const useFinanceData = () => {
  const { transactions, refreshData } = useFinance();

  const income = transactions.filter(t => t.type === 'income');
  const expenses = transactions.filter(t => t.type === 'expense');

  return {
    transactions,
    income,
    expenses,
    refreshData,
  };
};

export default useFinanceData;