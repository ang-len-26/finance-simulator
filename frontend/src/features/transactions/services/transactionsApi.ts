// =====================================================
// TRANSACTIONS API SERVICE
// Basado en TransactionViewSet y CategoryViewSet del backend
// Rama 3.1 - Transactions Module
// =====================================================

import apiClient from '@/services/api/client';
import { TRANSACTIONS_ENDPOINTS, buildUrlWithParams, buildTransactionFilters } from '@/services/api/endpoints';
import {
  Transaction,
  TransactionSummary,
  CreateTransactionData,
  UpdateTransactionData,
  TransactionFilters,
  TransactionDashboard,
  TransactionByType,
  TransactionSearchResult,
  RecentTransactionsResult,
  BudgetAlert,
  UnreadAlertsResult
} from '../types/transactions.types';
import { PaginatedResponse } from '@/types/api.types';

// =====================================================
// TRANSACTIONS CRUD API
// =====================================================

export const transactionsApi = {
  // ✅ CRUD básico
  list: async (filters?: TransactionFilters): Promise<PaginatedResponse<TransactionSummary>> => {
    const cleanFilters = filters ? buildTransactionFilters(filters) : {};
    const url = buildUrlWithParams(TRANSACTIONS_ENDPOINTS.TRANSACTIONS, cleanFilters);
    return await apiClient.get<PaginatedResponse<TransactionSummary>>(url);
  },

  create: async (data: CreateTransactionData): Promise<Transaction> => {
    return await apiClient.post<Transaction>(TRANSACTIONS_ENDPOINTS.TRANSACTIONS, data);
  },

  get: async (id: number): Promise<Transaction> => {
    return await apiClient.get<Transaction>(TRANSACTIONS_ENDPOINTS.TRANSACTION_DETAIL(id));
  },

  update: async (id: number, data: UpdateTransactionData): Promise<Transaction> => {
    return await apiClient.put<Transaction>(TRANSACTIONS_ENDPOINTS.TRANSACTION_DETAIL(id), data);
  },

  partialUpdate: async (id: number, data: Partial<UpdateTransactionData>): Promise<Transaction> => {
    return await apiClient.patch<Transaction>(TRANSACTIONS_ENDPOINTS.TRANSACTION_DETAIL(id), data);
  },

  delete: async (id: number): Promise<void> => {
    return await apiClient.delete<void>(TRANSACTIONS_ENDPOINTS.TRANSACTION_DETAIL(id));
  },

  // ✅ Custom actions - basados en @action del ViewSet
  getRecent: async (limit: number = 10): Promise<RecentTransactionsResult> => {
    const url = buildUrlWithParams(TRANSACTIONS_ENDPOINTS.TRANSACTION_RECENT, { limit });
    return await apiClient.get<RecentTransactionsResult>(url);
  },

  getByType: async (): Promise<TransactionByType> => {
    return await apiClient.get<TransactionByType>(TRANSACTIONS_ENDPOINTS.TRANSACTION_BY_TYPE);
  },

  search: async (query: string, limit: number = 20): Promise<TransactionSearchResult> => {
    const url = buildUrlWithParams(TRANSACTIONS_ENDPOINTS.TRANSACTION_SEARCH, { q: query, limit });
    return await apiClient.get<TransactionSearchResult>(url);
  },

  getDashboard: async (startDate?: string, endDate?: string): Promise<TransactionDashboard> => {
    const params: Record<string, any> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const url = buildUrlWithParams(TRANSACTIONS_ENDPOINTS.TRANSACTION_DASHBOARD, params);
    return await apiClient.get<TransactionDashboard>(url);
  },

  // ✅ Bulk operations
  bulkCreate: async (transactions: CreateTransactionData[]): Promise<Transaction[]> => {
    // Crear múltiples transacciones individualmente (el backend no tiene bulk endpoint)
    const promises = transactions.map(transaction => transactionsApi.create(transaction));
    return await Promise.all(promises);
  },

  bulkDelete: async (ids: number[]): Promise<void> => {
    const promises = ids.map(id => transactionsApi.delete(id));
    await Promise.all(promises);
  },

  // ✅ Utility functions
  validateTransaction: (data: CreateTransactionData): string[] => {
    const errors: string[] = [];
    
    if (!data.title?.trim()) {
      errors.push('El título es requerido');
    }
    
    if (!data.amount || parseFloat(data.amount) <= 0) {
      errors.push('El monto debe ser mayor que cero');
    }
    
    if (!data.type) {
      errors.push('El tipo de transacción es requerido');
    }
    
    if (!data.date) {
      errors.push('La fecha es requerida');
    }
    
    // Validaciones por tipo de transacción (basado en clean() del modelo)
    switch (data.type) {
      case 'income':
        if (!data.to_account) {
          errors.push('Los ingresos requieren una cuenta destino');
        }
        break;
      case 'expense':
        if (!data.from_account) {
          errors.push('Los gastos requieren una cuenta origen');
        }
        break;
      case 'transfer':
        if (!data.from_account) {
          errors.push('Las transferencias requieren una cuenta origen');
        }
        if (!data.to_account) {
          errors.push('Las transferencias requieren una cuenta destino');
        }
        if (data.from_account === data.to_account) {
          errors.push('No se puede transferir a la misma cuenta');
        }
        break;
      case 'investment':
      case 'debt':
      case 'savings':
        if (!data.from_account) {
          errors.push(`${data.type} requiere una cuenta origen`);
        }
        break;
    }
    
    return errors;
  },

  formatAmount: (amount: string | number): string => {
    const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
    return numAmount.toFixed(2);
  },

  getDisplayAmount: (transaction: Transaction | TransactionSummary): string => {
    const amount = parseFloat(transaction.amount);
    switch (transaction.type) {
      case 'income':
        return `+${amount.toFixed(2)}`;
      case 'expense':
        return `-${amount.toFixed(2)}`;
      default:
        return `${amount.toFixed(2)}`;
    }
  }
};

// =====================================================
// BUDGET ALERTS API
// =====================================================

export const budgetAlertsApi = {
  // ✅ ReadOnly operations basados en BudgetAlertViewSet
  list: async (): Promise<BudgetAlert[]> => {
    return await apiClient.get<BudgetAlert[]>(TRANSACTIONS_ENDPOINTS.BUDGET_ALERTS);
  },

  retrieve: async (id: number): Promise<BudgetAlert> => {
    return await apiClient.get<BudgetAlert>(TRANSACTIONS_ENDPOINTS.BUDGET_ALERT_DETAIL(id));
  },

  markAsRead: async (id: number): Promise<{ status: string }> => {
    return await apiClient.post<{ status: string }>(
      TRANSACTIONS_ENDPOINTS.BUDGET_ALERT_MARK_READ(id)
    );
  },

  getUnread: async (): Promise<UnreadAlertsResult> => {
    return await apiClient.get<UnreadAlertsResult>(TRANSACTIONS_ENDPOINTS.BUDGET_ALERTS_UNREAD);
  },

  // Utility function
  markMultipleAsRead: async (ids: number[]): Promise<void> => {
    const promises = ids.map(id => budgetAlertsApi.markAsRead(id));
    await Promise.all(promises);
  }
};