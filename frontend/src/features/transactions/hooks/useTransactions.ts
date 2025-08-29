// =====================================================
// useTransactions - Hook principal para gestión de transacciones
// Basado en TransactionViewSet del backend
// =====================================================

import { useState, useCallback, useEffect } from 'react';
import { useAsyncState } from '@/hooks/useAsyncState';
import { transactionsApi } from '../services/transactionsApi';
import { 
  Transaction, 
  TransactionSummary, 
  CreateTransactionData, 
  UpdateTransactionData, 
  TransactionFilters,
  TransactionDashboard,
  TransactionByType,
  TransactionSearchResult,
  RecentTransactionsResult 
} from '../types/transactions.types';
import { PaginatedResponse } from '@/types/api.types';

// =====================================================
// TIPOS INTERNOS DEL HOOK
// =====================================================

interface UseTransactionsState {
  transactions: TransactionSummary[];
  selectedTransaction: Transaction | null;
  totalCount: number;
  hasNextPage: boolean;
  currentPage: number;
}

interface UseTransactionsOptions {
  initialFilters?: TransactionFilters;
  autoLoad?: boolean;
  pageSize?: number;
}

interface UseTransactionsReturn {
  // Estado principal
  data: UseTransactionsState;
  isLoading: boolean;
  error: string | null;
  
  // Operaciones CRUD
  loadTransactions: (filters?: TransactionFilters) => Promise<void>;
  createTransaction: (data: CreateTransactionData) => Promise<Transaction>;
  updateTransaction: (id: number, data: UpdateTransactionData) => Promise<Transaction>;
  deleteTransaction: (id: number) => Promise<void>;
  getTransaction: (id: number) => Promise<Transaction>;
  
  // Operaciones de paginación
  loadNextPage: () => Promise<void>;
  loadPreviousPage: () => Promise<void>;
  goToPage: (page: number) => Promise<void>;
  
  // Operaciones especiales
  searchTransactions: (query: string) => Promise<TransactionSearchResult>;
  loadRecent: () => Promise<RecentTransactionsResult>;
  loadByType: () => Promise<TransactionByType>;
  loadDashboard: (startDate?: string, endDate?: string) => Promise<TransactionDashboard>;
  
  // Utilidades
  refreshTransactions: () => Promise<void>;
  clearError: () => void;
  setSelectedTransaction: (transaction: Transaction | null) => void;
}

// =====================================================
// HOOK PRINCIPAL
// =====================================================

export const useTransactions = (options: UseTransactionsOptions = {}): UseTransactionsReturn => {
  const {
    initialFilters = {},
    autoLoad = true,
    pageSize = 20
  } = options;

  const [asyncState, asyncActions] = useAsyncState<PaginatedResponse<TransactionSummary>>();
  const { data: asyncData, loading: isLoading, error } = asyncState;
  const { setData, setLoading, setError, reset } = asyncActions;

  // Estado local del hook
  const [state, setState] = useState<UseTransactionsState>({
    transactions: [],
    selectedTransaction: null,
    totalCount: 0,
    hasNextPage: false,
    currentPage: 1
  });

  // Filtros actuales
  const [currentFilters, setCurrentFilters] = useState<TransactionFilters>({
    ...initialFilters,
    page_size: pageSize
  });

  // Función helper para ejecutar operaciones async con manejo de errores
  const executeAsync = useCallback(async <T>(
    operation: () => Promise<T>
  ): Promise<T | null> => {
    try {
      setLoading(true);
      setError(null);
      const result = await operation();
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error inesperado';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError]);

  // =====================================================
  // ACCIONES PRINCIPALES CRUD
  // =====================================================

  const loadTransactions = useCallback(async (filters?: TransactionFilters) => {
    const finalFilters = filters ? { ...currentFilters, ...filters, page: 1 } : currentFilters;
    setCurrentFilters(finalFilters);

    const result = await executeAsync(() => transactionsApi.list(finalFilters));
    
    if (result) {
      setState(prev => ({
        ...prev,
        transactions: result.results,
        totalCount: result.count,
        hasNextPage: !!result.next,
        currentPage: 1
      }));
      setData(result);
    }
  }, [currentFilters, executeAsync, setData]);

  const loadNextPage = useCallback(async () => {
    if (!state.hasNextPage || isLoading) return;

    const nextPage = state.currentPage + 1;
    const filters = { ...currentFilters, page: nextPage };
    const result = await executeAsync(() => transactionsApi.list(filters));
    
    if (result) {
      setState(prev => ({
        ...prev,
        transactions: [...prev.transactions, ...result.results], // Acumular resultados
        hasNextPage: !!result.next,
        currentPage: nextPage
      }));
    }
  }, [state.hasNextPage, state.currentPage, currentFilters, executeAsync, isLoading]);

  const loadPreviousPage = useCallback(async () => {
    if (state.currentPage <= 1 || isLoading) return;

    const previousPage = state.currentPage - 1;
    const filters = { ...currentFilters, page: previousPage };
    const result = await executeAsync(() => transactionsApi.list(filters));
    
    if (result) {
      setState(prev => ({
        ...prev,
        transactions: result.results,
        hasNextPage: !!result.next,
        currentPage: previousPage
      }));
    }
  }, [state.currentPage, currentFilters, executeAsync, isLoading]);

  const goToPage = useCallback(async (page: number) => {
    if (page < 1 || isLoading) return;

    const filters = { ...currentFilters, page };
    const result = await executeAsync(() => transactionsApi.list(filters));
    
    if (result) {
      setState(prev => ({
        ...prev,
        transactions: result.results,
        hasNextPage: !!result.next,
        currentPage: page
      }));
    }
  }, [currentFilters, executeAsync, isLoading]);

  // =====================================================
  // OPERACIONES CRUD
  // =====================================================

  const createTransaction = useCallback(async (data: CreateTransactionData): Promise<Transaction> => {
    // Validar datos antes de enviar
    const validationErrors = transactionsApi.validateTransaction(data);
    if (validationErrors.length > 0) {
      throw new Error(`Errores de validación: ${validationErrors.join(', ')}`);
    }

    const result = await executeAsync(() => transactionsApi.create(data));
    
    if (!result) {
      throw new Error('Error al crear la transacción');
    }

    const newTransaction = result as Transaction;
    
    // Actualizar lista local agregando al principio
    setState(prev => ({
      ...prev,
      transactions: [
        {
          id: newTransaction.id,
          title: newTransaction.title,
          amount: newTransaction.amount,
          type: newTransaction.type,
          date: newTransaction.date,
          from_account_name: newTransaction.from_account_name,
          to_account_name: newTransaction.to_account_name,
          category_name: newTransaction.category_name,
          category_icon: newTransaction.category_icon,
          category_color: newTransaction.category_color,
          is_positive: newTransaction.type === 'income'
        },
        ...prev.transactions
      ].slice(0, pageSize), // Mantener el tamaño de página
      totalCount: prev.totalCount + 1
    }));

    return newTransaction;
  }, [pageSize, executeAsync]);

  const updateTransaction = useCallback(async (id: number, data: UpdateTransactionData): Promise<Transaction> => {

    const result = await executeAsync(() => transactionsApi.update(id, data));
    
    if (!result) {
      throw new Error('Error al actualizar la transacción');
    }

    const updatedTransaction = result as Transaction;
    
    // Actualizar en la lista local
    setState(prev => ({
      ...prev,
      transactions: prev.transactions.map(t => 
        t.id === id 
          ? {
              ...t,
              title: updatedTransaction.title,
              amount: updatedTransaction.amount,
              type: updatedTransaction.type,
              date: updatedTransaction.date,
              from_account_name: updatedTransaction.from_account_name,
              to_account_name: updatedTransaction.to_account_name,
              category_name: updatedTransaction.category_name,
              category_icon: updatedTransaction.category_icon,
              category_color: updatedTransaction.category_color,
              is_positive: updatedTransaction.type === 'income'
            }
          : t
      ),
      selectedTransaction: prev.selectedTransaction?.id === id ? updatedTransaction : prev.selectedTransaction
    }));

    return updatedTransaction;
  }, [executeAsync]);

  const deleteTransaction = useCallback(async (id: number): Promise<void> => {

    const result = await executeAsync(() => transactionsApi.delete(id));
    
    if (result === null && error) {
      throw new Error('Error al eliminar la transacción');
    }
    
    // Remover de la lista local
    setState(prev => ({
      ...prev,
      transactions: prev.transactions.filter(t => t.id !== id),
      totalCount: Math.max(0, prev.totalCount - 1),
      selectedTransaction: prev.selectedTransaction?.id === id ? null : prev.selectedTransaction
    }));
  }, [executeAsync, error]);

  const getTransaction = useCallback(async (id: number): Promise<Transaction> => {
    
    const result = await executeAsync(() => transactionsApi.get(id));
    
    if (!result) {
      throw new Error('Error al obtener la transacción');
    }

    const transaction = result as Transaction;
    
    setState(prev => ({
      ...prev,
      selectedTransaction: transaction
    }));

    return transaction;
  }, [executeAsync]);

  // =====================================================
  // OPERACIONES ESPECIALES
  // =====================================================

  const searchTransactions = useCallback(async (query: string): Promise<TransactionSearchResult> => {
    
    const result = await executeAsync(() => transactionsApi.search(query));
    
    if (!result) {
      throw new Error('Error en la búsqueda');
    }

    return result as TransactionSearchResult;
  }, [executeAsync]);

  const loadRecent = useCallback(async (): Promise<RecentTransactionsResult> => {
    
    const result = await executeAsync(() => transactionsApi.getRecent());
    
    if (!result) {
      throw new Error('Error al cargar transacciones recientes');
    }

    return result as RecentTransactionsResult;
  }, [executeAsync]);

  const loadByType = useCallback(async (): Promise<TransactionByType> => {
    
    const result = await executeAsync(() => transactionsApi.getByType());
    
    if (!result) {
      throw new Error('Error al cargar transacciones por tipo');
    }

    return result as TransactionByType;
  }, [executeAsync]);

  const loadDashboard = useCallback(async (startDate?: string, endDate?: string): Promise<TransactionDashboard> => {
    // CORRIGIDO: crear objeto de parámetros correctamente
    const params: Record<string, string> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const result = await executeAsync(() => transactionsApi.getDashboard(params.start_date, params.end_date));
    
    if (!result) {
      throw new Error('Error al cargar dashboard');
    }

    return result as TransactionDashboard;
  }, [executeAsync]);

  // =====================================================
  // UTILIDADES
  // =====================================================

  const refreshTransactions = useCallback(async () => {
    await loadTransactions(currentFilters);
  }, [loadTransactions, currentFilters]);

  const setSelectedTransaction = useCallback((transaction: Transaction | null) => {
    setState(prev => ({
      ...prev,
      selectedTransaction: transaction
    }));
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, [setError]);

  // =====================================================
  // EFECTOS
  // =====================================================

  useEffect(() => {
    if (autoLoad) {
      loadTransactions();
    }
  }, []); // Solo ejecutar al montar, evitar dependencias que causen loops

  // =====================================================
  // RETURN
  // =====================================================

  return {
    // Estado
    data: state,
    isLoading,
    error,
    
    // CRUD
    loadTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    getTransaction,
    
    // Paginación
    loadNextPage,
    loadPreviousPage,
    goToPage,
    
    // Especiales
    searchTransactions,
    loadRecent,
    loadByType,
    loadDashboard,
    
    // Utilidades
    refreshTransactions,
    clearError,
    setSelectedTransaction
  };
};

export default useTransactions;