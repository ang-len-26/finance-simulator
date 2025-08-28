import apiClient from '@/services/api/client';
import { 
  Account, 
  AccountSummary, 
  CreateAccountData, 
  UpdateAccountData,
  AccountFilters,
  AccountsSummaryResponse,
  BalanceHistoryPoint,
  ReconcileAccountData,
  ReconcileResponse
} from '../types/accounts.types';
import { PaginatedResponse } from '@/types/api.types';

// =====================================================
// ACCOUNTS API SERVICE - Métodos específicos para cuentas
// Basado en AccountViewSet y endpoints reales del backend
// =====================================================

export const accountsApi = {
  // =====================================================
  // CRUD OPERATIONS
  // =====================================================

  /**
   * Obtener lista de cuentas del usuario
   * GET /api/accounts/
   */
  getAccounts: async (filters?: AccountFilters): Promise<PaginatedResponse<AccountSummary>> => {
    const params = filters ? { ...filters } : {};
    return apiClient.get<PaginatedResponse<AccountSummary>>('/accounts/', { params });
  },

  /**
   * Obtener cuenta específica por ID
   * GET /api/accounts/{id}/
   */
  getAccount: async (id: number): Promise<Account> => {
    return apiClient.get<Account>(`/accounts/${id}/`);
  },

  /**
   * Crear nueva cuenta
   * POST /api/accounts/
   */
  createAccount: async (data: CreateAccountData): Promise<Account> => {
    return apiClient.post<Account>('/accounts/', data);
  },

  /**
   * Actualizar cuenta completa
   * PUT /api/accounts/{id}/
   */
  updateAccount: async (id: number, data: CreateAccountData): Promise<Account> => {
    return apiClient.put<Account>(`/accounts/${id}/`, data);
  },

  /**
   * Actualizar cuenta parcialmente
   * PATCH /api/accounts/{id}/
   */
  updateAccountPartial: async (id: number, data: UpdateAccountData): Promise<Account> => {
    return apiClient.patch<Account>(`/accounts/${id}/`, data);
  },

  /**
   * Eliminar cuenta
   * DELETE /api/accounts/{id}/
   */
  deleteAccount: async (id: number): Promise<void> => {
    return apiClient.delete<void>(`/accounts/${id}/`);
  },

  // =====================================================
  // CUSTOM ENDPOINTS (basados en @action del ViewSet)
  // =====================================================

  /**
   * Obtener resumen financiero de todas las cuentas
   * GET /api/accounts/summary/
   */
  getAccountsSummary: async (): Promise<AccountsSummaryResponse> => {
    return apiClient.get<AccountsSummaryResponse>('/accounts/summary/');
  },

  /**
   * Obtener transacciones de una cuenta específica
   * GET /api/accounts/{id}/transactions/
   */
  getAccountTransactions: async (accountId: number, filters?: any): Promise<any[]> => {
    const params = filters ? { ...filters } : {};
    return apiClient.get<any[]>(`/accounts/${accountId}/transactions/`, { params });
  },

  /**
   * Obtener historial de balance de una cuenta (últimos 30 días)
   * GET /api/accounts/{id}/balance_history/
   */
  getBalanceHistory: async (accountId: number): Promise<BalanceHistoryPoint[]> => {
    return apiClient.get<BalanceHistoryPoint[]>(`/accounts/${accountId}/balance_history/`);
  },

  /**
   * Conciliar cuenta con balance real
   * POST /api/accounts/{id}/reconcile/
   */
  reconcileAccount: async (
    accountId: number, 
    data: ReconcileAccountData
  ): Promise<ReconcileResponse> => {
    return apiClient.post<ReconcileResponse>(`/accounts/${accountId}/reconcile/`, data);
  },

  // =====================================================
  // UTILITY METHODS
  // =====================================================

  /**
   * Obtener cuentas activas solamente
   */
  getActiveAccounts: async (): Promise<PaginatedResponse<AccountSummary>> => {
    return accountsApi.getAccounts({ is_active: true });
  },

  /**
   * Obtener cuentas por tipo
   */
  getAccountsByType: async (accountType: string): Promise<PaginatedResponse<AccountSummary>> => {
    return accountsApi.getAccounts({ account_type: accountType as any });
  },

  /**
   * Buscar cuentas por nombre
   */
  searchAccounts: async (searchTerm: string): Promise<PaginatedResponse<AccountSummary>> => {
    return accountsApi.getAccounts({ name: searchTerm });
  },

  /**
   * Obtener cuentas con rango de balance
   */
  getAccountsByBalanceRange: async (
    minBalance?: number, 
    maxBalance?: number
  ): Promise<PaginatedResponse<AccountSummary>> => {
    return accountsApi.getAccounts({ 
      min_balance: minBalance,
      max_balance: maxBalance
    });
  },

  /**
   * Obtener cuentas sin transacciones
   */
  getUnusedAccounts: async (): Promise<PaginatedResponse<AccountSummary>> => {
    return accountsApi.getAccounts({ has_transactions: false });
  },

  // =====================================================
  // BATCH OPERATIONS
  // =====================================================

  /**
   * Activar/desactivar múltiples cuentas
   */
  toggleAccountsStatus: async (accountIds: number[], isActive: boolean): Promise<Account[]> => {
    const promises = accountIds.map(id => 
      accountsApi.updateAccountPartial(id, { is_active: isActive })
    );
    return Promise.all(promises);
  },

  /**
   * Obtener múltiples cuentas por IDs
   */
  getMultipleAccounts: async (accountIds: number[]): Promise<Account[]> => {
    const promises = accountIds.map(id => accountsApi.getAccount(id));
    return Promise.all(promises);
  },

  // =====================================================
  // VALIDATION HELPERS
  // =====================================================

  /**
   * Validar si un nombre de cuenta está disponible
   * (se hace en el frontend para dar feedback inmediato)
   */
  validateAccountName: async (name: string, excludeId?: number): Promise<boolean> => {
    try {
      const response = await accountsApi.getAccounts({ name });
      // Si existe y no es la cuenta que estamos editando
      const existingAccount = response.results.find(acc => 
        acc.name.toLowerCase() === name.toLowerCase() && acc.id !== excludeId
      );
      return !existingAccount; // true si está disponible
    } catch {
      return true; // En caso de error, asumir disponible
    }
  },

  /**
   * Verificar si una cuenta tiene transacciones antes de eliminar
   */
  checkAccountHasTransactions: async (accountId: number): Promise<boolean> => {
    try {
      const account = await accountsApi.getAccount(accountId);
      return account.transaction_count > 0;
    } catch {
      return false;
    }
  }
};

export default accountsApi;