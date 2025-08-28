import { useState, useEffect, useCallback, useMemo } from 'react';
import { accountsApi } from '../services/accountsApi';
import { BalanceHistoryPoint } from '../types/accounts.types';
import { ApiError } from '@/types/api.types';

// =====================================================
// TYPES
// =====================================================

interface BalanceHistoryStats {
  highest: { date: string; balance: number };
  lowest: { date: string; balance: number };
  average: number;
  trend: 'increasing' | 'decreasing' | 'stable';
  totalChange: number;
  percentageChange: number;
}

interface UseBalanceHistoryReturn {
  // Data
  history: BalanceHistoryPoint[];
  stats: BalanceHistoryStats | null;
  
  // State
  isLoading: boolean;
  error: ApiError | null;
  
  // Operations
  refetch: () => Promise<void>;
  
  // Utilities
  getBalanceAtDate: (date: string) => number | null;
  getDateRange: () => { start: string; end: string } | null;
  hasData: boolean;
  
  // Chart helpers
  chartData: Array<{ x: string; y: number }>;
  formatBalance: (value: number) => string;
  formatDate: (date: string) => string;
}

interface UseBalanceHistoryOptions {
  accountId?: number;
  autoRefresh?: boolean;
  refreshInterval?: number; // in milliseconds
  currency?: string;
}

// =====================================================
// HOOK
// =====================================================

export const useBalanceHistory = (
  options: UseBalanceHistoryOptions = {}
): UseBalanceHistoryReturn => {
  
  const {
    accountId,
    autoRefresh = false,
    refreshInterval = 5 * 60 * 1000, // 5 minutes
    currency = 'PEN'
  } = options;

  // State
  const [history, setHistory] = useState<BalanceHistoryPoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  // =====================================================
  // COMPUTED VALUES
  // =====================================================

  const hasData = useMemo(() => history.length > 0, [history]);

  const stats = useMemo((): BalanceHistoryStats | null => {
    if (history.length === 0) return null;

    const balances = history.map(point => point.balance);
    const highest = history.reduce((max, point) => 
      point.balance > max.balance ? point : max
    );
    const lowest = history.reduce((min, point) => 
      point.balance < min.balance ? point : min
    );

    const average = balances.reduce((sum, balance) => sum + balance, 0) / balances.length;
    
    // Calculate trend
    const firstBalance = history[0].balance;
    const lastBalance = history[history.length - 1].balance;
    const totalChange = lastBalance - firstBalance;
    const percentageChange = firstBalance === 0 ? 0 : (totalChange / firstBalance) * 100;
    
    let trend: 'increasing' | 'decreasing' | 'stable' = 'stable';
    if (Math.abs(percentageChange) > 1) { // 1% threshold for stability
      trend = percentageChange > 0 ? 'increasing' : 'decreasing';
    }

    return {
      highest,
      lowest,
      average,
      trend,
      totalChange,
      percentageChange
    };
  }, [history]);

  const chartData = useMemo(() => {
    return history.map(point => ({
      x: point.date,
      y: point.balance
    }));
  }, [history]);

  // =====================================================
  // FETCH OPERATIONS
  // =====================================================

  const fetchHistory = useCallback(async () => {
    if (!accountId) {
      setError({ message: 'Account ID is required' });
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      const historyData = await accountsApi.getBalanceHistory(accountId);
      setHistory(historyData);
    } catch (error) {
      setError(error as ApiError);
      setHistory([]);
    } finally {
      setIsLoading(false);
    }
  }, [accountId]);

  // =====================================================
  // UTILITIES
  // =====================================================

  const getBalanceAtDate = useCallback((date: string): number | null => {
    const point = history.find(p => p.date === date);
    return point ? point.balance : null;
  }, [history]);

  const getDateRange = useCallback((): { start: string; end: string } | null => {
    if (history.length === 0) return null;
    return {
      start: history[0].date,
      end: history[history.length - 1].date
    };
  }, [history]);

  // =====================================================
  // FORMATTING HELPERS
  // =====================================================

  const formatBalance = useCallback((value: number): string => {
    const formatter = new Intl.NumberFormat('es-PE', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    
    return formatter.format(value);
  }, [currency]);

  const formatDate = useCallback((date: string): string => {
    const dateObj = new Date(date);
    return dateObj.toLocaleDateString('es-PE', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  }, []);

  // =====================================================
  // EFFECTS
  // =====================================================

  useEffect(() => {
    if (accountId) {
      fetchHistory();
    }
  }, [accountId, fetchHistory]);

  // Auto refresh effect
  useEffect(() => {
    if (!autoRefresh || !accountId) return;

    const interval = setInterval(() => {
      fetchHistory();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, accountId, refreshInterval, fetchHistory]);

  // =====================================================
  // RETURN
  // =====================================================

  return {
    // Data
    history,
    stats,
    
    // State
    isLoading,
    error,
    
    // Operations
    refetch: fetchHistory,
    
    // Utilities
    getBalanceAtDate,
    getDateRange,
    hasData,
    
    // Chart helpers
    chartData,
    formatBalance,
    formatDate,
  };
};

// =====================================================
// MULTI ACCOUNT BALANCE HISTORY HOOK
// =====================================================

interface UseMultiAccountBalanceHistoryReturn {
  accountsHistory: Record<number, BalanceHistoryPoint[]>;
  combinedHistory: BalanceHistoryPoint[];
  isLoading: boolean;
  errors: Record<number, ApiError>;
  refetchAll: () => Promise<void>;
  refetchAccount: (accountId: number) => Promise<void>;
  getTotalBalanceAtDate: (date: string) => number;
  getAccountBalanceAtDate: (accountId: number, date: string) => number | null;
}

interface UseMultiAccountBalanceHistoryOptions {
  accountIds: number[];
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export const useMultiAccountBalanceHistory = (
  options: UseMultiAccountBalanceHistoryOptions
): UseMultiAccountBalanceHistoryReturn => {
  
  const { accountIds, autoRefresh = false, refreshInterval = 5 * 60 * 1000 } = options;

  const [accountsHistory, setAccountsHistory] = useState<Record<number, BalanceHistoryPoint[]>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<number, ApiError>>({});

  // =====================================================
  // COMPUTED VALUES
  // =====================================================

  const combinedHistory = useMemo((): BalanceHistoryPoint[] => {
    const dateMap = new Map<string, number>();
    
    // Combine all account histories by date
    Object.entries(accountsHistory).forEach(([accountId, history]) => {
      history.forEach(point => {
        const currentBalance = dateMap.get(point.date) || 0;
        dateMap.set(point.date, currentBalance + point.balance);
      });
    });
    
    // Convert to array and sort by date
    const combined = Array.from(dateMap.entries())
      .map(([date, balance]) => ({ date, balance }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    
    return combined;
  }, [accountsHistory]);

  // =====================================================
  // FETCH OPERATIONS
  // =====================================================

  const fetchAccountHistory = useCallback(async (accountId: number) => {
    try {
      const history = await accountsApi.getBalanceHistory(accountId);
      
      setAccountsHistory(prev => ({
        ...prev,
        [accountId]: history
      }));
      
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[accountId];
        return newErrors;
      });
      
    } catch (error) {
      setErrors(prev => ({
        ...prev,
        [accountId]: error as ApiError
      }));
    }
  }, []);

  const refetchAll = useCallback(async () => {
    setIsLoading(true);
    
    try {
      await Promise.all(
        accountIds.map(accountId => fetchAccountHistory(accountId))
      );
    } finally {
      setIsLoading(false);
    }
  }, [accountIds, fetchAccountHistory]);

  const refetchAccount = useCallback(async (accountId: number) => {
    await fetchAccountHistory(accountId);
  }, [fetchAccountHistory]);

  // =====================================================
  // UTILITIES
  // =====================================================

  const getTotalBalanceAtDate = useCallback((date: string): number => {
    return Object.values(accountsHistory).reduce((total, history) => {
      const point = history.find(p => p.date === date);
      return total + (point ? point.balance : 0);
    }, 0);
  }, [accountsHistory]);

  const getAccountBalanceAtDate = useCallback((accountId: number, date: string): number | null => {
    const history = accountsHistory[accountId];
    if (!history) return null;
    
    const point = history.find(p => p.date === date);
    return point ? point.balance : null;
  }, [accountsHistory]);

  // =====================================================
  // EFFECTS
  // =====================================================

  useEffect(() => {
    if (accountIds.length > 0) {
      refetchAll();
    }
  }, [accountIds, refetchAll]);

  // Auto refresh effect
  useEffect(() => {
    if (!autoRefresh || accountIds.length === 0) return;

    const interval = setInterval(() => {
      refetchAll();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, accountIds, refreshInterval, refetchAll]);

  // =====================================================
  // RETURN
  // =====================================================

  return {
    accountsHistory,
    combinedHistory,
    isLoading,
    errors,
    refetchAll,
    refetchAccount,
    getTotalBalanceAtDate,
    getAccountBalanceAtDate,
  };
};

// =====================================================
// BALANCE RECONCILIATION HOOK
// =====================================================

interface UseBalanceReconciliationReturn {
  reconcile: (accountId: number, realBalance: number) => Promise<boolean>;
  isReconciling: boolean;
  lastReconciliation: {
    accountId: number;
    difference: number;
    timestamp: string;
  } | null;
  error: ApiError | null;
}

export const useBalanceReconciliation = (): UseBalanceReconciliationReturn => {
  const [isReconciling, setIsReconciling] = useState(false);
  const [lastReconciliation, setLastReconciliation] = useState<{
    accountId: number;
    difference: number;
    timestamp: string;
  } | null>(null);
  const [error, setError] = useState<ApiError | null>(null);

  const reconcile = useCallback(async (accountId: number, realBalance: number): Promise<boolean> => {
    try {
      setIsReconciling(true);
      setError(null);
      
      const result = await accountsApi.reconcileAccount(accountId, { real_balance: realBalance.toString() });
      
      setLastReconciliation({
        accountId,
        difference: result.difference,
        timestamp: new Date().toISOString()
      });
      
      return true;
    } catch (error) {
      setError(error as ApiError);
      return false;
    } finally {
      setIsReconciling(false);
    }
  }, []);

  return {
    reconcile,
    isReconciling,
    lastReconciliation,
    error,
  };
};