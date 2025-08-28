import { PaginationParams } from "@/types/api.types";

// =====================================================
// ACCOUNT TYPES - Basado en accounts/models.py y serializers.py
// =====================================================

// Tipos de cuenta (DEBE coincidir con Account.ACCOUNT_TYPES en models.py)
export type AccountType = 
  | 'checking'        // Cuenta Corriente
  | 'savings'         // Cuenta Ahorros  
  | 'investment'      // Cuenta Inversión
  | 'credit'          // Tarjeta Crédito
  | 'cash'            // Efectivo
  | 'digital_wallet'  // Billetera Digital
  | 'business'        // Cuenta Empresarial
  | 'other';          // Otros

// Monedas válidas (debe coincidir con validate_currency en serializers.py)
export type Currency = 'PEN' | 'USD' | 'EUR';

// =====================================================
// ACCOUNT INTERFACES
// =====================================================

// Account completa (basada en AccountSerializer)
export interface Account {
  id: number;
  name: string;
  bank_name: string;
  account_number: string;
  account_type: AccountType;
  initial_balance: string;      // Decimal como string
  current_balance: string;      // Decimal como string (read-only)
  currency: Currency;
  is_active: boolean;
  include_in_reports: boolean;
  transaction_count: number;    // SerializerMethodField
  last_transaction_date: string | null; // SerializerMethodField
  monthly_income: number;       // SerializerMethodField (float)
  monthly_expenses: number;     // SerializerMethodField (float)
  created_at: string;          // ISO datetime
  updated_at: string;          // ISO datetime
}

// Account ligera para listados (basada en AccountSummarySerializer)
export interface AccountSummary {
  id: number;
  name: string;
  bank_name: string;
  account_type: AccountType;
  current_balance: string;
  currency: Currency;
  is_active: boolean;
}

// =====================================================
// REQUEST/RESPONSE TYPES
// =====================================================

// Datos para crear cuenta
export interface CreateAccountData {
  name: string;
  bank_name?: string;           // Optional en el modelo
  account_number?: string;      // Optional en el modelo
  account_type: AccountType;
  initial_balance: string;      // Decimal como string
  currency: Currency;
  is_active?: boolean;         // Default true
  include_in_reports?: boolean; // Default true
}

// Datos para actualizar cuenta
export interface UpdateAccountData extends Partial<CreateAccountData> {}

// Respuesta del endpoint /accounts/summary/ (basada en views.py)
export interface AccountsSummaryResponse {
  total_balance: number;
  total_accounts: number;
  balance_by_type: Record<AccountType, number>;
  most_used_accounts: Array<{
    id: number;
    name: string;
    bank_name: string;
    account_type: AccountType;
    transaction_count: number;
    balance: number;
  }>;
}

// Punto de historial de balance (basado en balance_history action)
export interface BalanceHistoryPoint {
  date: string;    // YYYY-MM-DD format
  balance: number; // float
}

// Datos para conciliación (basado en reconcile action)
export interface ReconcileAccountData {
  real_balance: string; // Decimal como string
}

// Respuesta de conciliación
export interface ReconcileResponse {
  message: string;
  difference: number;
  new_balance: number;
}

// =====================================================
// FILTER TYPES
// =====================================================

// Filtros de cuentas (basado en AccountFilter en filters.py)
export interface AccountFilters extends PaginationParams {
  // Filtros de texto
  name?: string;               // icontains
  bank_name?: string;          // icontains
  
  // Filtros de selección
  account_type?: AccountType | AccountType[];  // Puede ser múltiple
  currency?: Currency;         // iexact
  
  // Filtros numéricos
  min_balance?: number;        // gte
  max_balance?: number;        // lte
  
  // Filtros booleanos
  is_active?: boolean;
  include_in_reports?: boolean;
  has_transactions?: boolean;  // Custom filter
}

// =====================================================
// UI HELPER TYPES
// =====================================================

// Opciones para select de tipo de cuenta
export interface AccountTypeOption {
  value: AccountType;
  label: string;
  icon?: string;
}

// Opciones para select de moneda
export interface CurrencyOption {
  value: Currency;
  label: string;
  symbol: string;
}

// Estado de cuenta para UI
export interface AccountUIState {
  isLoading: boolean;
  isUpdating: boolean;
  hasError: boolean;
  errorMessage?: string;
}

// =====================================================
// CONSTANTS
// =====================================================

// Etiquetas para tipos de cuenta (para UI)
export const ACCOUNT_TYPE_LABELS: Record<AccountType, string> = {
  checking: 'Cuenta Corriente',
  savings: 'Cuenta Ahorros',
  investment: 'Cuenta Inversión', 
  credit: 'Tarjeta Crédito',
  cash: 'Efectivo',
  digital_wallet: 'Billetera Digital',
  business: 'Cuenta Empresarial',
  other: 'Otros'
};

// Etiquetas para monedas
export const CURRENCY_LABELS: Record<Currency, { label: string; symbol: string }> = {
  PEN: { label: 'Soles Peruanos', symbol: 'S/' },
  USD: { label: 'Dólares', symbol: '$' },
  EUR: { label: 'Euros', symbol: '€' }
};

// =====================================================
// VALIDATION TYPES
// =====================================================

// Reglas de validación para cuenta
export interface AccountValidationRules {
  name: {
    required: boolean;
    minLength: number;
    maxLength: number;
  };
  initial_balance: {
    required: boolean;
    min: number;
  };
  account_type: {
    required: boolean;
    allowedValues: AccountType[];
  };
  currency: {
    required: boolean;
    allowedValues: Currency[];
  };
}

// Resultado de validación de cuenta
export interface AccountValidationResult {
  isValid: boolean;
  errors: Partial<Record<keyof CreateAccountData, string>>;
}