// =====================================================
// INDEX - Exportaciones centralizadas de hooks de transactions
// =====================================================

// Hooks principales
export { default as useTransactions } from './useTransactions';
export { default as useCategories } from './useCategories';
export { default as useTransactionFilters } from './useTransactionFilters';
export { default as useBudgetAlerts, useAlertNotifications } from './useBudgetAlerts';

// Re-exportar tipos si son necesarios en otros módulos
export type {
  // De useTransactions
  UseTransactionsReturn,
  UseTransactionsOptions,
  
  // De useCategories  
  UseCategoriesReturn,
  UseCategoriesOptions,
  
  // De useTransactionFilters
  UseTransactionFiltersReturn,
  UseTransactionFiltersOptions,
  
  // De useBudgetAlerts
  UseBudgetAlertsReturn,
  UseBudgetAlertsOptions,
  UseAlertNotificationsOptions
} from './useTransactions';

// Nota: Los tipos específicos están en cada archivo individual
// Esta exportación es para facilitar imports desde otros módulos