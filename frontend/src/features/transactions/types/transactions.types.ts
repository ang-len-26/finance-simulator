// =====================================================
// TIPOS DE TRANSACTIONS - Basados en models.py y serializers.py reales
// Rama 3 - Transactions Module
// =====================================================

import { DateRangeFilter, PaginationParams } from "@/types/api.types";

// =====================================================
// TIPOS DE ENUMS - Exactos del backend
// =====================================================

// Basado en Transaction.TRANSACTION_TYPES del modelo
export type TransactionType = 
  | 'income' 
  | 'expense' 
  | 'transfer' 
  | 'investment' 
  | 'loan' 
  | 'debt' 
  | 'savings' 
  | 'other';

// Basado en Category.CATEGORY_TYPES del modelo
export type CategoryType = 'income' | 'expense' | 'both';

// Basado en Transaction.recurring_frequency choices del modelo
export type RecurringFrequency = 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';

// Basado en TransactionFilter.cash_flow choices
export type CashFlowType = 'positive' | 'negative' | 'internal';

// =====================================================
// CATEGORY INTERFACES - Basadas en CategorySerializer
// =====================================================

export interface Category {
  id: number;
  name: string;
  slug: string;
  icon: string;                           // lucide-react icon name
  color: string;                          // hex color (#6366f1)
  category_type: CategoryType;
  parent: number | null;
  parent_name: string | null;
  is_active: boolean;
  sort_order: number;
  transaction_count: number;              // Computed field
  subcategories: CategorySummary[];       // Nested subcategories
  created_at: string;
  updated_at: string;
}

export interface CategorySummary {
  id: number;
  name: string;
  icon: string;
  color: string;
  category_type: CategoryType;
}

export interface CreateCategoryData {
  name: string;
  icon?: string;
  color?: string;
  category_type: CategoryType;
  parent?: number;
  sort_order?: number;
}

export interface UpdateCategoryData extends Partial<CreateCategoryData> {
  is_active?: boolean;
}

// =====================================================
// TRANSACTION INTERFACES - Basadas en TransactionSerializer
// =====================================================

export interface Transaction {
  id: number;
  title: string;
  amount: string;                         // DecimalField como string
  type: TransactionType;
  date: string;                          // YYYY-MM-DD format
  description: string;
  
  // Account relationships - pueden ser null según el tipo
  from_account: number | null;
  to_account: number | null;
  from_account_name: string | null;      // Read-only field
  to_account_name: string | null;        // Read-only field
  
  // Category relationship - con información extendida
  category: number | null;
  category_name: string | null;          // Read-only field
  category_icon: string | null;          // Read-only field
  category_color: string | null;         // Read-only field
  
  // Additional fields del modelo
  reference_number: string;              // Número de referencia/voucher
  location: string;                      // Lugar de la transacción
  tags: string[];                        // JSONField como array
  
  // Recurrence fields
  is_recurring: boolean;
  recurring_frequency: RecurringFrequency | null;
  parent_transaction: number | null;     // FK a transacción padre
  
  // Metadata
  created_at: string;
  updated_at: string;
}

export interface TransactionSummary {
  id: number;
  title: string;
  amount: string;
  type: TransactionType;
  date: string;
  from_account_name: string | null;
  to_account_name: string | null;
  category_name: string | null;
  category_icon: string | null;
  category_color: string | null;
  is_positive: boolean;                  // Computed field
}

export interface CreateTransactionData {
  title: string;
  amount: string;                        // Como string para precisión decimal
  type: TransactionType;
  date: string;                          // YYYY-MM-DD
  description?: string;
  
  // Accounts - requeridos según tipo de transacción
  from_account?: number;
  to_account?: number;
  
  // Category
  category?: number;
  
  // Optional fields
  reference_number?: string;
  location?: string;
  tags?: string[];
  
  // Recurrence
  is_recurring?: boolean;
  recurring_frequency?: RecurringFrequency;
}

export interface UpdateTransactionData extends Partial<CreateTransactionData> {}

// =====================================================
// BUDGET ALERTS - Basadas en BudgetAlertSerializer
// =====================================================

export interface BudgetAlert {
  id: number;
  user: number;
  title: string;
  message: string;
  alert_type: string;                    // Tipo de alerta
  severity: 'info' | 'warning' | 'error';
  is_read: boolean;
  created_at: string;
  updated_at: string;
}

// =====================================================
// FILTROS - Basados en TransactionFilter del backend
// =====================================================

export interface TransactionFilters extends PaginationParams, DateRangeFilter {
  // Filtros básicos
  type?: TransactionType;
  min_amount?: number;
  max_amount?: number;
  description?: string;                  // Búsqueda en descripción/título
  
  // Filtros de cuentas
  from_account?: number;
  to_account?: number;
  account?: number;                      // Cualquier cuenta (origen O destino)
  bank?: string;                         // Nombre del banco
  account_type?: string;                 // Tipo de cuenta
  
  // Filtros de categorías
  category?: number;
  
  // Filtros adicionales
  has_reference?: boolean;               // Con/sin número de referencia
  location?: string;                     // Ubicación
  tags?: string[];                       // Etiquetas
  
  // Filtros de recurrencia
  is_recurring?: boolean;
  recurring_frequency?: RecurringFrequency;
  
  // Filtro de flujo de efectivo
  cash_flow?: CashFlowType;
  
  // Búsqueda general
  search?: string;                       // Para endpoint /search/
}

export interface CategoryFilters extends PaginationParams {
  is_active?: boolean;
  category_type?: CategoryType;
  parent?: number | null;                // null para categorías padre
}

// =====================================================
// RESPONSES DE ENDPOINTS - Basados en views.py
// =====================================================

export interface TransactionDashboard {
  period: {
    start_date: string;
    end_date: string;
  };
  metrics: {
    total_income: number;
    total_expenses: number;
    total_investments: number;
    total_savings: number;
    net_flow: number;
    transaction_count: number;
  };
  top_expense_accounts: Array<{
    account: string;
    bank: string;
    total: number;
  }>;
  top_income_accounts: Array<{
    account: string;
    bank: string;
    total: number;
  }>;
}

export interface TransactionByType {
  [key: string]: {
    label: string;
    count: number;
    transactions: TransactionSummary[];
  };
}

export interface TransactionSearchResult {
  query: string;
  results: TransactionSummary[];
  count: number;
}

export interface RecentTransactionsResult {
  transactions: TransactionSummary[];
  total_count: number;
}

// =====================================================
// CATEGORY ENDPOINTS RESPONSES
// =====================================================

export interface CategoriesByType {
  income: CategorySummary[];
  expense: CategorySummary[];
}

export interface CategoryHierarchy extends Category {
  subcategories: CategorySummary[];
}

export interface CategoryTransactionsResult {
  transactions: TransactionSummary[];
  statistics: {
    total_amount: number;
    transaction_count: number;
    average_amount: number;
    max_amount: number;
    min_amount: number;
  };
}

export interface CategoryMonthlyTrend {
  category: CategorySummary;
  trend_data: Array<{
    month: string;                       // YYYY-MM
    month_label: string;                 // "Jan 2024"
    amount: number;
    transaction_count: number;
  }>;
  period: {
    start_date: string;
    end_date: string;
  };
}

export interface CategoryStatistics {
  period: {
    start_date: string;
    end_date: string;
  };
  most_used_categories: Array<{
    name: string;
    icon: string;
    color: string;
    type: CategoryType;
    total_amount: number;
    transaction_count: number;
    average_amount: number;
  }>;
  summary: {
    total_categories_used: number;
    uncategorized_transactions: number;
    total_active_categories: number;
  };
}

// =====================================================
// BUDGET ALERTS RESPONSES
// =====================================================

export interface UnreadAlertsResult {
  unread_alerts: BudgetAlert[];
  count: number;
  message: string;
}

// =====================================================
// FORM DATA INTERFACES
// =====================================================

export interface TransactionFormData {
  title: string;
  amount: number | '';
  type: TransactionType | '';
  date: string;
  description: string;
  from_account: number | '';
  to_account: number | '';
  category: number | '';
  reference_number: string;
  location: string;
  tags: string[];
  is_recurring: boolean;
  recurring_frequency: RecurringFrequency | '';
}

export interface CategoryFormData {
  name: string;
  icon: string;
  color: string;
  category_type: CategoryType | '';
  parent: number | '';
  sort_order: number | '';
}

// =====================================================
// UTILITY TYPES
// =====================================================

export interface TransactionTypeOption {
  value: TransactionType;
  label: string;
  description: string;
  requires_from_account: boolean;
  requires_to_account: boolean;
  icon: string;
}

export interface CategoryTypeOption {
  value: CategoryType;
  label: string;
  description: string;
  icon: string;
}

// =====================================================
// CONSTANTS PARA UI
// =====================================================

export const TRANSACTION_TYPE_OPTIONS: TransactionTypeOption[] = [
  {
    value: 'income',
    label: 'Ingreso',
    description: 'Dinero que entra a una cuenta',
    requires_from_account: false,
    requires_to_account: true,
    icon: 'TrendingUp'
  },
  {
    value: 'expense',
    label: 'Gasto',
    description: 'Dinero que sale de una cuenta',
    requires_from_account: true,
    requires_to_account: false,
    icon: 'TrendingDown'
  },
  {
    value: 'transfer',
    label: 'Transferencia',
    description: 'Movimiento entre cuentas propias',
    requires_from_account: true,
    requires_to_account: true,
    icon: 'ArrowRightLeft'
  },
  {
    value: 'investment',
    label: 'Inversión',
    description: 'Compra de activos de inversión',
    requires_from_account: true,
    requires_to_account: false,
    icon: 'LineChart'
  },
  {
    value: 'loan',
    label: 'Préstamo',
    description: 'Dinero prestado a terceros',
    requires_from_account: true,
    requires_to_account: false,
    icon: 'HandCoins'
  },
  {
    value: 'debt',
    label: 'Deuda',
    description: 'Pago de deuda o préstamo',
    requires_from_account: true,
    requires_to_account: false,
    icon: 'CreditCard'
  },
  {
    value: 'savings',
    label: 'Ahorro',
    description: 'Dinero apartado para ahorros',
    requires_from_account: true,
    requires_to_account: false,
    icon: 'PiggyBank'
  },
  {
    value: 'other',
    label: 'Otro',
    description: 'Otros tipos de transacciones',
    requires_from_account: false,
    requires_to_account: false,
    icon: 'MoreHorizontal'
  }
];

export const CATEGORY_TYPE_OPTIONS: CategoryTypeOption[] = [
  {
    value: 'income',
    label: 'Ingreso',
    description: 'Para transacciones de entrada de dinero',
    icon: 'TrendingUp'
  },
  {
    value: 'expense',
    label: 'Gasto',
    description: 'Para transacciones de salida de dinero',
    icon: 'TrendingDown'
  },
  {
    value: 'both',
    label: 'Ambos',
    description: 'Puede usarse para ingresos y gastos',
    icon: 'ArrowUpDown'
  }
];

export const RECURRING_FREQUENCY_OPTIONS = [
  { value: 'daily', label: 'Diario' },
  { value: 'weekly', label: 'Semanal' },
  { value: 'monthly', label: 'Mensual' },
  { value: 'quarterly', label: 'Trimestral' },
  { value: 'yearly', label: 'Anual' }
] as const;

export const CASH_FLOW_OPTIONS = [
  { value: 'positive', label: 'Entradas de dinero' },
  { value: 'negative', label: 'Salidas de dinero' },
  { value: 'internal', label: 'Movimientos internos' }
] as const;