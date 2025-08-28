import { useState, useEffect, useCallback } from 'react';
import { accountsApi } from '../services/accountsApi';
import { 
  Account, 
  AccountSummary, 
  CreateAccountData, 
  UpdateAccountData,
  AccountsSummaryResponse,
  AccountFilters
} from '../types/accounts.types';
import { ApiError, PaginatedResponse } from '@/types/api.types';

// =====================================================
// TYPES
// =====================================================

interface UseAccountsState {
  accounts: AccountSummary[];
  totalCount: number;
  isLoading: boolean;
  error: ApiError | null;
  hasNextPage: boolean;
  hasPrevPage: boolean;
}

interface UseAccountsReturn extends UseAccountsState {
  // CRUD operations
  createAccount: (data: CreateAccountData) => Promise<Account | null>;
  updateAccount: (id: number, data: UpdateAccountData) => Promise<Account | null>;
  deleteAccount: (id: number) => Promise<boolean>;
  getAccountById: (id: number) => Promise<Account | null>;
  
  // Data operations
  refetch: () => Promise<void>;
  loadMore: () => Promise<void>;
  refresh: () => Promise<void>;
  
  // Filter operations
  applyFilters: (filters: AccountFilters) => Promise<void>;
  clearFilters: () => Promise<void>;
  
  // State helpers
  isCreating: boolean;
  isUpdating: boolean;
  isDeleting: boolean;
}

interface UseAccountsOptions {
  initialFilters?: AccountFilters;
  autoLoad?: boolean;
  pageSize?: number;
}

// =====================================================
// HOOK
// =====================================================

export const useAccounts = (options: UseAccountsOptions = {}): UseAccountsReturn => {
  const {
    initialFilters = {},
    autoLoad = true,
    pageSize = 10
  } = options;

  // State
  const [state, setState] = useState<UseAccountsState>({
    accounts: [],
    totalCount: 0,
    isLoading: false,
    error: null,
    hasNextPage: false,
    hasPrevPage: false,
  });

  const [currentFilters, setCurrentFilters] = useState<AccountFilters>({
    ...initialFilters,
    page_size: pageSize
  });

  const [currentPage, setCurrentPage] = useState(1);
  
  // Operation states
  const [isCreating, setIsCreating] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // =====================================================
  // FETCH OPERATIONS
  // =====================================================

  const fetchAccounts = useCallback(async (
    filters: AccountFilters = currentFilters,
    page: number = 1,
    append: boolean = false
  ) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      const response: PaginatedResponse<AccountSummary> = await accountsApi.getAccounts({
        ...filters,
        page,
        page_size: filters.page_size || pageSize
      });

      setState(prev => ({
        ...prev,
        accounts: append ? [...prev.accounts, ...response.results] : response.results,
        totalCount: response.count,
        hasNextPage: !!response.next,
        hasPrevPage: !!response.previous,
        isLoading: false
      }));

      setCurrentPage(page);
      setCurrentFilters(filters);

    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error as ApiError,
        isLoading: false
      }));
    }
  }, [currentFilters, pageSize]);

  // =====================================================
  // CRUD OPERATIONS
  // =====================================================

  const createAccount = useCallback(async (data: CreateAccountData): Promise<Account | null> => {
    try {
      setIsCreating(true);
      setState(prev => ({ ...prev, error: null }));

      const newAccount = await accountsApi.createAccount(data);
      
      // Refresh list after creation
      await fetchAccounts(currentFilters, 1, false);
      
      return newAccount;
    } catch (error) {
      setState(prev => ({ ...prev, error: error as ApiError }));
      return null;
    } finally {
      setIsCreating(false);
    }
  }, [currentFilters, fetchAccounts]);

  const updateAccount = useCallback(async (
    id: number, 
    data: UpdateAccountData
  ): Promise<Account | null> => {
    try {
      setIsUpdating(true);
      setState(prev => ({ ...prev, error: null }));

      const updatedAccount = await accountsApi.updateAccount(id, data as CreateAccountData);
      
      // Update account in current list if exists
      setState(prev => ({
        ...prev,
        accounts: prev.accounts.map(account => 
          account.id === id 
            ? { ...account, ...data } as AccountSummary
            : account
        )
      }));
      
      return updatedAccount;
    } catch (error) {
      setState(prev => ({ ...prev, error: error as ApiError }));
      return null;
    } finally {
      setIsUpdating(false);
    }
  }, []);

  const deleteAccount = useCallback(async (id: number): Promise<boolean> => {
    try {
      setIsDeleting(true);
      setState(prev => ({ ...prev, error: null }));

      await accountsApi.deleteAccount(id);
      
      // Remove from current list
      setState(prev => ({
        ...prev,
        accounts: prev.accounts.filter(account => account.id !== id),
        totalCount: prev.totalCount - 1
      }));
      
      return true;
    } catch (error) {
      setState(prev => ({ ...prev, error: error as ApiError }));
      return false;
    } finally {
      setIsDeleting(false);
    }
  }, []);

  const getAccountById = useCallback(async (id: number): Promise<Account | null> => {
    try {
      setState(prev => ({ ...prev, error: null }));
      return await accountsApi.getAccount(id);
    } catch (error) {
      setState(prev => ({ ...prev, error: error as ApiError }));
      return null;
    }
  }, []);

  // =====================================================
  // DATA OPERATIONS
  // =====================================================

  const refetch = useCallback(async (): Promise<void> => {
    await fetchAccounts(currentFilters, currentPage, false);
  }, [fetchAccounts, currentFilters, currentPage]);

  const loadMore = useCallback(async (): Promise<void> => {
    if (state.hasNextPage && !state.isLoading) {
      await fetchAccounts(currentFilters, currentPage + 1, true);
    }
  }, [fetchAccounts, currentFilters, currentPage, state.hasNextPage, state.isLoading]);

  const refresh = useCallback(async (): Promise<void> => {
    await fetchAccounts(currentFilters, 1, false);
  }, [fetchAccounts, currentFilters]);

  // =====================================================
  // FILTER OPERATIONS
  // =====================================================

  const applyFilters = useCallback(async (filters: AccountFilters): Promise<void> => {
    await fetchAccounts(filters, 1, false);
  }, [fetchAccounts]);

  const clearFilters = useCallback(async (): Promise<void> => {
    const cleanFilters: AccountFilters = { page_size: pageSize };
    await fetchAccounts(cleanFilters, 1, false);
  }, [fetchAccounts, pageSize]);

  // =====================================================
  // EFFECTS
  // =====================================================

  useEffect(() => {
    if (autoLoad) {
      fetchAccounts();
    }
  }, [autoLoad, fetchAccounts]);

  // =====================================================
  // RETURN
  // =====================================================

  return {
    // State
    ...state,
    
    // CRUD operations
    createAccount,
    updateAccount,
    deleteAccount,
    getAccountById,
    
    // Data operations
    refetch,
    loadMore,
    refresh,
    
    // Filter operations
    applyFilters,
    clearFilters,
    
    // Operation states
    isCreating,
    isUpdating,
    isDeleting,
  };
};

// =====================================================
// SINGLE ACCOUNT HOOK
// =====================================================

interface UseSingleAccountReturn {
  account: Account | null;
  isLoading: boolean;
  error: ApiError | null;
  refetch: () => Promise<void>;
  update: (data: UpdateAccountData) => Promise<Account | null>;
  delete: () => Promise<boolean>;
}

export const useSingleAccount = (accountId: number): UseSingleAccountReturn => {
  const [account, setAccount] = useState<Account | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const fetchAccount = useCallback(async () => {
    if (!accountId) return;
    
    try {
      setIsLoading(true);
      setError(null);
      const accountData = await accountsApi.getAccount(accountId);
      setAccount(accountData);
    } catch (error) {
      setError(error as ApiError);
    } finally {
      setIsLoading(false);
    }
  }, [accountId]);

  const updateAccount = useCallback(async (data: UpdateAccountData): Promise<Account | null> => {
    try {
      setError(null);
      const updatedAccount = await accountsApi.updateAccount(accountId, data as CreateAccountData);
      setAccount(updatedAccount);
      return updatedAccount;
    } catch (error) {
      setError(error as ApiError);
      return null;
    }
  }, [accountId]);

  const deleteAccount = useCallback(async (): Promise<boolean> => {
    try {
      setError(null);
      await accountsApi.deleteAccount(accountId);
      setAccount(null);
      return true;
    } catch (error) {
      setError(error as ApiError);
      return false;
    }
  }, [accountId]);

  useEffect(() => {
    fetchAccount();
  }, [fetchAccount]);

  return {
    account,
    isLoading,
    error,
    refetch: fetchAccount,
    update: updateAccount,
    delete: deleteAccount,
  };
};

// =====================================================
// ACCOUNTS SUMMARY HOOK
// =====================================================

interface UseAccountsSummaryReturn {
  summary: AccountsSummaryResponse | null;
  isLoading: boolean;
  error: ApiError | null;
  refetch: () => Promise<void>;
}

export const useAccountsSummary = (): UseAccountsSummaryReturn => {
  const [summary, setSummary] = useState<AccountsSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const fetchSummary = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const summaryData = await accountsApi.getAccountsSummary();
      setSummary(summaryData);
    } catch (error) {
      setError(error as ApiError);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  return {
    summary,
    isLoading,
    error,
    refetch: fetchSummary,
  };
};