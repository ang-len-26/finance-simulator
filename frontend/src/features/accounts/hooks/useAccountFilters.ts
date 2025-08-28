import { useState, useCallback, useMemo } from 'react';
import { 
  AccountFilters, 
  AccountType, 
  Currency,
  ACCOUNT_TYPE_LABELS,
  CURRENCY_LABELS 
} from '../types/accounts.types';
import { AccountTypeOption, CurrencyOption } from '../types/accounts.types';

// =====================================================
// TYPES
// =====================================================

interface FilterOption {
  value: string | number | boolean;
  label: string;
  count?: number;
}

interface UseAccountFiltersReturn {
  // Current filters
  filters: AccountFilters;
  
  // Filter operations
  setFilter: <K extends keyof AccountFilters>(key: K, value: AccountFilters[K]) => void;
  removeFilter: (key: keyof AccountFilters) => void;
  clearAllFilters: () => void;
  resetToDefaults: () => void;
  
  // Filter utilities
  hasActiveFilters: boolean;
  activeFilterCount: number;
  getFilterSummary: () => string;
  
  // Search operations
  setSearchTerm: (term: string) => void;
  clearSearch: () => void;
  
  // Range filters
  setBalanceRange: (min?: number, max?: number) => void;
  clearBalanceRange: () => void;
  
  // Multiple selection filters
  toggleAccountType: (type: AccountType) => void;
  setAccountTypes: (types: AccountType[]) => void;
  clearAccountTypes: () => void;
  selectedAccountTypes: AccountType[];
  
  // Boolean filters
  toggleActiveOnly: () => void;
  toggleReportsOnly: () => void;
  toggleWithTransactions: () => void;
  
  // Options for UI
  accountTypeOptions: AccountTypeOption[];
  currencyOptions: CurrencyOption[];
  
  // Validation
  isValidFilter: (key: keyof AccountFilters, value: any) => boolean;
  getFilterErrors: () => Partial<Record<keyof AccountFilters, string>>;
}

interface UseAccountFiltersOptions {
  defaultFilters?: Partial<AccountFilters>;
  onFiltersChange?: (filters: AccountFilters) => void;
  debounceMs?: number;
}

// =====================================================
// HOOK
// =====================================================

export const useAccountFilters = (
  options: UseAccountFiltersOptions = {}
): UseAccountFiltersReturn => {
  
  const {
    defaultFilters = {},
    onFiltersChange,
    debounceMs = 300
  } = options;

  // Default filter state
  const initialFilters: AccountFilters = {
    page: 1,
    page_size: 10,
    ...defaultFilters
  };

  const [filters, setFilters] = useState<AccountFilters>(initialFilters);

  // =====================================================
  // COMPUTED VALUES
  // =====================================================

  const hasActiveFilters = useMemo(() => {
    const filterKeys = Object.keys(filters) as Array<keyof AccountFilters>;
    return filterKeys.some(key => {
      if (['page', 'page_size', 'ordering'].includes(key)) return false;
      const value = filters[key];
      return value !== undefined && value !== null && value !== '';
    });
  }, [filters]);

  const activeFilterCount = useMemo(() => {
    const filterKeys = Object.keys(filters) as Array<keyof AccountFilters>;
    return filterKeys.filter(key => {
      if (['page', 'page_size', 'ordering'].includes(key)) return false;
      const value = filters[key];
      return value !== undefined && value !== null && value !== '';
    }).length;
  }, [filters]);

  const selectedAccountTypes = useMemo(() => {
    const types = filters.account_type;
    if (!types) return [];
    return Array.isArray(types) ? types : [types];
  }, [filters.account_type]);

  // UI Options
  const accountTypeOptions: AccountTypeOption[] = useMemo(() => {
    return Object.entries(ACCOUNT_TYPE_LABELS).map(([value, label]) => ({
      value: value as AccountType,
      label,
      icon: getAccountTypeIcon(value as AccountType)
    }));
  }, []);

  const currencyOptions: CurrencyOption[] = useMemo(() => {
    return Object.entries(CURRENCY_LABELS).map(([value, config]) => ({
      value: value as Currency,
      label: config.label,
      symbol: config.symbol
    }));
  }, []);

  // =====================================================
  // FILTER OPERATIONS
  // =====================================================

  const updateFilters = useCallback((newFilters: AccountFilters) => {
    setFilters(newFilters);
    onFiltersChange?.(newFilters);
  }, [onFiltersChange]);

  const setFilter = useCallback(<K extends keyof AccountFilters>(
    key: K, 
    value: AccountFilters[K]
  ) => {
    const newFilters = { ...filters, [key]: value, page: 1 }; // Reset page when filtering
    updateFilters(newFilters);
  }, [filters, updateFilters]);

  const removeFilter = useCallback((key: keyof AccountFilters) => {
    const newFilters = { ...filters };
    delete newFilters[key];
    newFilters.page = 1; // Reset page
    updateFilters(newFilters);
  }, [filters, updateFilters]);

  const clearAllFilters = useCallback(() => {
    const cleanFilters: AccountFilters = {
      page: 1,
      page_size: filters.page_size || 10
    };
    updateFilters(cleanFilters);
  }, [filters.page_size, updateFilters]);

  const resetToDefaults = useCallback(() => {
    updateFilters(initialFilters);
  }, [initialFilters, updateFilters]);

  // =====================================================
  // SEARCH OPERATIONS
  // =====================================================

  const setSearchTerm = useCallback((term: string) => {
    const newFilters = { 
      ...filters, 
      name: term.trim() || undefined,
      page: 1 
    };
    updateFilters(newFilters);
  }, [filters, updateFilters]);

  const clearSearch = useCallback(() => {
    const newFilters = { ...filters };
    delete newFilters.name;
    delete newFilters.bank_name;
    newFilters.page = 1;
    updateFilters(newFilters);
  }, [filters, updateFilters]);

  // =====================================================
  // RANGE FILTERS
  // =====================================================

  const setBalanceRange = useCallback((min?: number, max?: number) => {
    const newFilters = { 
      ...filters, 
      min_balance: min,
      max_balance: max,
      page: 1 
    };
    updateFilters(newFilters);
  }, [filters, updateFilters]);

  const clearBalanceRange = useCallback(() => {
    const newFilters = { ...filters };
    delete newFilters.min_balance;
    delete newFilters.max_balance;
    newFilters.page = 1;
    updateFilters(newFilters);
  }, [filters, updateFilters]);

  // =====================================================
  // MULTIPLE SELECTION FILTERS
  // =====================================================

  const toggleAccountType = useCallback((type: AccountType) => {
    const currentTypes = selectedAccountTypes;
    const newTypes = currentTypes.includes(type)
      ? currentTypes.filter(t => t !== type)
      : [...currentTypes, type];
    
    const newFilters = { 
      ...filters, 
      account_type: newTypes.length > 0 ? newTypes : undefined,
      page: 1 
    };
    updateFilters(newFilters);
  }, [selectedAccountTypes, filters, updateFilters]);

  const setAccountTypes = useCallback((types: AccountType[]) => {
    const newFilters = { 
      ...filters, 
      account_type: types.length > 0 ? types : undefined,
      page: 1 
    };
    updateFilters(newFilters);
  }, [filters, updateFilters]);

  const clearAccountTypes = useCallback(() => {
    const newFilters = { ...filters };
    delete newFilters.account_type;
    newFilters.page = 1;
    updateFilters(newFilters);
  }, [filters, updateFilters]);

  // =====================================================
  // BOOLEAN FILTERS
  // =====================================================

  const toggleActiveOnly = useCallback(() => {
    const newValue = filters.is_active === true ? undefined : true;
    setFilter('is_active', newValue);
  }, [filters.is_active, setFilter]);

  const toggleReportsOnly = useCallback(() => {
    const newValue = filters.include_in_reports === true ? undefined : true;
    setFilter('include_in_reports', newValue);
  }, [filters.include_in_reports, setFilter]);

  const toggleWithTransactions = useCallback(() => {
    const newValue = filters.has_transactions === true ? undefined : true;
    setFilter('has_transactions', newValue);
  }, [filters.has_transactions, setFilter]);

  // =====================================================
  // UTILITIES
  // =====================================================

  const getFilterSummary = useCallback((): string => {
    const summaryParts: string[] = [];
    
    if (filters.name) summaryParts.push(`Nombre: "${filters.name}"`);
    if (filters.bank_name) summaryParts.push(`Banco: "${filters.bank_name}"`);
    if (filters.account_type) {
      const types = Array.isArray(filters.account_type) ? filters.account_type : [filters.account_type];
      const typeLabels = types.map(type => ACCOUNT_TYPE_LABELS[type]);
      summaryParts.push(`Tipo: ${typeLabels.join(', ')}`);
    }
    if (filters.currency) summaryParts.push(`Moneda: ${CURRENCY_LABELS[filters.currency].label}`);
    if (filters.min_balance !== undefined) summaryParts.push(`Balance mín: ${filters.min_balance}`);
    if (filters.max_balance !== undefined) summaryParts.push(`Balance máx: ${filters.max_balance}`);
    if (filters.is_active === true) summaryParts.push('Solo activas');
    if (filters.include_in_reports === true) summaryParts.push('En reportes');
    if (filters.has_transactions === true) summaryParts.push('Con transacciones');
    if (filters.has_transactions === false) summaryParts.push('Sin transacciones');
    
    return summaryParts.join(' • ');
  }, [filters]);

  const isValidFilter = useCallback((key: keyof AccountFilters, value: any): boolean => {
    switch (key) {
      case 'min_balance':
      case 'max_balance':
        return typeof value === 'number' && value >= 0;
      
      case 'account_type':
        if (Array.isArray(value)) {
          return value.every(type => Object.keys(ACCOUNT_TYPE_LABELS).includes(type));
        }
        return Object.keys(ACCOUNT_TYPE_LABELS).includes(value);
      
      case 'currency':
        return Object.keys(CURRENCY_LABELS).includes(value);
      
      case 'is_active':
      case 'include_in_reports':
      case 'has_transactions':
        return typeof value === 'boolean';
      
      case 'name':
      case 'bank_name':
        return typeof value === 'string' && value.trim().length > 0;
      
      case 'page':
      case 'page_size':
        return typeof value === 'number' && value > 0;
      
      default:
        return true;
    }
  }, []);

  const getFilterErrors = useCallback((): Partial<Record<keyof AccountFilters, string>> => {
    const errors: Partial<Record<keyof AccountFilters, string>> = {};
    
    if (filters.min_balance !== undefined && filters.max_balance !== undefined) {
      if (filters.min_balance > filters.max_balance) {
        errors.min_balance = 'El balance mínimo no puede ser mayor al máximo';
        errors.max_balance = 'El balance máximo no puede ser menor al mínimo';
      }
    }
    
    if (filters.min_balance !== undefined && filters.min_balance < 0) {
      errors.min_balance = 'El balance mínimo no puede ser negativo';
    }
    
    if (filters.max_balance !== undefined && filters.max_balance < 0) {
      errors.max_balance = 'El balance máximo no puede ser negativo';
    }
    
    return errors;
  }, [filters]);

  // =====================================================
  // RETURN
  // =====================================================

  return {
    // Current filters
    filters,
    
    // Filter operations
    setFilter,
    removeFilter,
    clearAllFilters,
    resetToDefaults,
    
    // Filter utilities
    hasActiveFilters,
    activeFilterCount,
    getFilterSummary,
    
    // Search operations
    setSearchTerm,
    clearSearch,
    
    // Range filters
    setBalanceRange,
    clearBalanceRange,
    
    // Multiple selection filters
    toggleAccountType,
    setAccountTypes,
    clearAccountTypes,
    selectedAccountTypes,
    
    // Boolean filters
    toggleActiveOnly,
    toggleReportsOnly,
    toggleWithTransactions,
    
    // Options for UI
    accountTypeOptions,
    currencyOptions,
    
    // Validation
    isValidFilter,
    getFilterErrors,
  };
};

// =====================================================
// HELPER FUNCTIONS
// =====================================================

const getAccountTypeIcon = (type: AccountType): string => {
  const iconMap: Record<AccountType, string> = {
    checking: '🏦',
    savings: '💰',
    investment: '📈',
    credit: '💳',
    cash: '💵',
    digital_wallet: '📱',
    business: '🏢',
    other: '📋'
  };
  
  return iconMap[type] || '📋';
};