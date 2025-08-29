// =====================================================
// useTransactionFilters - Hook para filtros avanzados de transacciones
// Basado en TransactionFilter del backend
// =====================================================

import { useState, useCallback, useMemo } from 'react';
import { 
  TransactionFilters, 
  TransactionType, 
  RecurringFrequency, 
  CashFlowType 
} from '../types/transactions.types';

// =====================================================
// TIPOS INTERNOS DEL HOOK
// =====================================================

interface FilterState {
  // Filtros básicos
  type: TransactionType | '';
  min_amount: number | '';
  max_amount: number | '';
  description: string;
  
  // Filtros de fechas
  date_after: string;
  date_before: string;
  
  // Filtros de cuentas
  from_account: number | '';
  to_account: number | '';
  account: number | '';  // Cualquier cuenta
  bank: string;
  account_type: string;
  
  // Filtros de categorías
  category: number | '';
  
  // Filtros adicionales
  has_reference: boolean | null;
  location: string;
  tags: string[];
  
  // Filtros de recurrencia
  is_recurring: boolean | null;
  recurring_frequency: RecurringFrequency | '';
  
  // Filtro de flujo de efectivo
  cash_flow: CashFlowType | '';
  
  // Búsqueda general
  search: string;
}

interface UseTransactionFiltersOptions {
  initialFilters?: Partial<FilterState>;
  onFiltersChange?: (filters: TransactionFilters) => void;
}

interface UseTransactionFiltersReturn {
  // Estado de filtros
  filters: FilterState;
  
  // Métodos individuales de filtros
  setType: (type: TransactionType | '') => void;
  setAmountRange: (min?: number, max?: number) => void;
  setDescription: (description: string) => void;
  setDateRange: (startDate?: string, endDate?: string) => void;
  setFromAccount: (accountId: number | '') => void;
  setToAccount: (accountId: number | '') => void;
  setAnyAccount: (accountId: number | '') => void;
  setBank: (bank: string) => void;
  setAccountType: (accountType: string) => void;
  setCategory: (categoryId: number | '') => void;
  setHasReference: (hasReference: boolean | null) => void;
  setLocation: (location: string) => void;
  setTags: (tags: string[]) => void;
  addTag: (tag: string) => void;
  removeTag: (tag: string) => void;
  setIsRecurring: (isRecurring: boolean | null) => void;
  setRecurringFrequency: (frequency: RecurringFrequency | '') => void;
  setCashFlow: (cashFlow: CashFlowType | '') => void;
  setSearch: (search: string) => void;
  
  // Operaciones en lote
  updateFilters: (newFilters: Partial<FilterState>) => void;
  clearAllFilters: () => void;
  clearDateFilters: () => void;
  clearAmountFilters: () => void;
  clearAccountFilters: () => void;
  
  // Utilidades
  getActiveFilters: () => TransactionFilters;
  getActiveFilterCount: () => number;
  hasActiveFilters: () => boolean;
  exportFiltersAsQuery: () => string;
  
  // Presets comunes
  applyLastWeekFilter: () => void;
  applyLastMonthFilter: () => void;
  applyThisMonthFilter: () => void;
  applyIncomeOnlyFilter: () => void;
  applyExpensesOnlyFilter: () => void;
  applyTransfersOnlyFilter: () => void;
  
  // Validaciones
  isValidAmountRange: () => boolean;
  isValidDateRange: () => boolean;
}

// =====================================================
// HOOK PRINCIPAL
// =====================================================

export const useTransactionFilters = (options: UseTransactionFiltersOptions = {}): UseTransactionFiltersReturn => {
  const { initialFilters = {}, onFiltersChange } = options;

  // Estado inicial de los filtros
  const defaultFilters: FilterState = {
    type: '',
    min_amount: '',
    max_amount: '',
    description: '',
    date_after: '',
    date_before: '',
    from_account: '',
    to_account: '',
    account: '',
    bank: '',
    account_type: '',
    category: '',
    has_reference: null,
    location: '',
    tags: [],
    is_recurring: null,
    recurring_frequency: '',
    cash_flow: '',
    search: ''
  };

  const [filters, setFilters] = useState<FilterState>({
    ...defaultFilters,
    ...initialFilters
  });

  // =====================================================
  // MÉTODOS INDIVIDUALES DE FILTROS
  // =====================================================

  const updateFilter = useCallback((newFilters: Partial<FilterState>) => {
    setFilters(prev => {
      const updated = { ...prev, ...newFilters };
      
      // Notificar cambio si hay callback
      if (onFiltersChange) {
        const activeFilters = buildActiveFilters(updated);
        onFiltersChange(activeFilters);
      }
      
      return updated;
    });
  }, [onFiltersChange]);

  const setType = useCallback((type: TransactionType | '') => {
    updateFilter({ type });
  }, [updateFilter]);

  const setAmountRange = useCallback((min?: number, max?: number) => {
    updateFilter({ 
      min_amount: min ?? '', 
      max_amount: max ?? '' 
    });
  }, [updateFilter]);

  const setDescription = useCallback((description: string) => {
    updateFilter({ description });
  }, [updateFilter]);

  const setDateRange = useCallback((startDate?: string, endDate?: string) => {
    updateFilter({ 
      date_after: startDate || '', 
      date_before: endDate || '' 
    });
  }, [updateFilter]);

  const setFromAccount = useCallback((accountId: number | '') => {
    updateFilter({ from_account: accountId });
  }, [updateFilter]);

  const setToAccount = useCallback((accountId: number | '') => {
    updateFilter({ to_account: accountId });
  }, [updateFilter]);

  const setAnyAccount = useCallback((accountId: number | '') => {
    updateFilter({ account: accountId });
  }, [updateFilter]);

  const setBank = useCallback((bank: string) => {
    updateFilter({ bank });
  }, [updateFilter]);

  const setAccountType = useCallback((accountType: string) => {
    updateFilter({ account_type: accountType });
  }, [updateFilter]);

  const setCategory = useCallback((categoryId: number | '') => {
    updateFilter({ category: categoryId });
  }, [updateFilter]);

  const setHasReference = useCallback((hasReference: boolean | null) => {
    updateFilter({ has_reference: hasReference });
  }, [updateFilter]);

  const setLocation = useCallback((location: string) => {
    updateFilter({ location });
  }, [updateFilter]);

  const setTags = useCallback((tags: string[]) => {
    updateFilter({ tags });
  }, [updateFilter]);

  const addTag = useCallback((tag: string) => {
    if (!tag.trim() || filters.tags.includes(tag)) return;
    
    updateFilter({ tags: [...filters.tags, tag.trim()] });
  }, [filters.tags, updateFilter]);

  const removeTag = useCallback((tag: string) => {
    updateFilter({ tags: filters.tags.filter(t => t !== tag) });
  }, [filters.tags, updateFilter]);

  const setIsRecurring = useCallback((isRecurring: boolean | null) => {
    updateFilter({ is_recurring: isRecurring });
  }, [updateFilter]);

  const setRecurringFrequency = useCallback((frequency: RecurringFrequency | '') => {
    updateFilter({ recurring_frequency: frequency });
  }, [updateFilter]);

  const setCashFlow = useCallback((cashFlow: CashFlowType | '') => {
    updateFilter({ cash_flow: cashFlow });
  }, [updateFilter]);

  const setSearch = useCallback((search: string) => {
    updateFilter({ search });
  }, [updateFilter]);

  // =====================================================
  // OPERACIONES EN LOTE
  // =====================================================

  const updateFilters = useCallback((newFilters: Partial<FilterState>) => {
    updateFilter(newFilters);
  }, [updateFilter]);

  const clearAllFilters = useCallback(() => {
    setFilters(defaultFilters);
    if (onFiltersChange) {
      onFiltersChange({});
    }
  }, [onFiltersChange]);

  const clearDateFilters = useCallback(() => {
    updateFilter({ date_after: '', date_before: '' });
  }, [updateFilter]);

  const clearAmountFilters = useCallback(() => {
    updateFilter({ min_amount: '', max_amount: '' });
  }, [updateFilter]);

  const clearAccountFilters = useCallback(() => {
    updateFilter({ 
      from_account: '', 
      to_account: '', 
      account: '', 
      bank: '', 
      account_type: '' 
    });
  }, [updateFilter]);

  // =====================================================
  // UTILIDADES
  // =====================================================

  const buildActiveFilters = useCallback((filterState: FilterState): TransactionFilters => {
    const active: TransactionFilters = {};

    // Filtros básicos
    if (filterState.type) active.type = filterState.type as TransactionType;
    if (filterState.min_amount !== '') active.min_amount = Number(filterState.min_amount);
    if (filterState.max_amount !== '') active.max_amount = Number(filterState.max_amount);
    if (filterState.description.trim()) active.description = filterState.description.trim();
    
    // Filtros de fechas
    if (filterState.date_after) active.date_after = filterState.date_after;
    if (filterState.date_before) active.date_before = filterState.date_before;
    
    // Filtros de cuentas
    if (filterState.from_account !== '') active.from_account = Number(filterState.from_account);
    if (filterState.to_account !== '') active.to_account = Number(filterState.to_account);
    if (filterState.account !== '') active.account = Number(filterState.account);
    if (filterState.bank.trim()) active.bank = filterState.bank.trim();
    if (filterState.account_type.trim()) active.account_type = filterState.account_type.trim();
    
    // Filtros de categorías
    if (filterState.category !== '') active.category = Number(filterState.category);
    
    // Filtros adicionales
    if (filterState.has_reference !== null) active.has_reference = filterState.has_reference;
    if (filterState.location.trim()) active.location = filterState.location.trim();
    if (filterState.tags.length > 0) active.tags = filterState.tags;
    
    // Filtros de recurrencia
    if (filterState.is_recurring !== null) active.is_recurring = filterState.is_recurring;
    if (filterState.recurring_frequency) active.recurring_frequency = filterState.recurring_frequency as RecurringFrequency;
    
    // Filtro de flujo de efectivo
    if (filterState.cash_flow) active.cash_flow = filterState.cash_flow as CashFlowType;
    
    // Búsqueda general
    if (filterState.search.trim()) active.search = filterState.search.trim();

    return active;
  }, []);

  const getActiveFilters = useCallback((): TransactionFilters => {
    return buildActiveFilters(filters);
  }, [filters, buildActiveFilters]);

  const getActiveFilterCount = useCallback((): number => {
    const active = getActiveFilters();
    return Object.keys(active).length;
  }, [getActiveFilters]);

  const hasActiveFilters = useCallback((): boolean => {
    return getActiveFilterCount() > 0;
  }, [getActiveFilterCount]);

  const exportFiltersAsQuery = useCallback((): string => {
    const active = getActiveFilters();
    const params = new URLSearchParams();

    Object.entries(active).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          params.append(key, value.join(','));
        } else {
          params.append(key, String(value));
        }
      }
    });

    return params.toString();
  }, [getActiveFilters]);

  // =====================================================
  // PRESETS COMUNES
  // =====================================================

  const applyLastWeekFilter = useCallback(() => {
    const today = new Date();
    const lastWeek = new Date(today);
    lastWeek.setDate(today.getDate() - 7);

    setDateRange(lastWeek.toISOString().split('T')[0], today.toISOString().split('T')[0]);
  }, [setDateRange]);

  const applyLastMonthFilter = useCallback(() => {
    const today = new Date();
    const lastMonth = new Date(today);
    lastMonth.setMonth(today.getMonth() - 1);

    setDateRange(lastMonth.toISOString().split('T')[0], today.toISOString().split('T')[0]);
  }, [setDateRange]);

  const applyThisMonthFilter = useCallback(() => {
    const today = new Date();
    const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);

    setDateRange(firstDayOfMonth.toISOString().split('T')[0], today.toISOString().split('T')[0]);
  }, [setDateRange]);

  const applyIncomeOnlyFilter = useCallback(() => {
    setType('income');
    setCashFlow('positive');
  }, [setType, setCashFlow]);

  const applyExpensesOnlyFilter = useCallback(() => {
    setType('expense');
    setCashFlow('negative');
  }, [setType, setCashFlow]);

  const applyTransfersOnlyFilter = useCallback(() => {
    setType('transfer');
    setCashFlow('internal');
  }, [setType, setCashFlow]);

  // =====================================================
  // VALIDACIONES
  // =====================================================

  const isValidAmountRange = useCallback((): boolean => {
    const min = filters.min_amount;
    const max = filters.max_amount;
    
    if (min === '' || max === '') return true; // Si uno está vacío, es válido
    
    return Number(min) <= Number(max);
  }, [filters.min_amount, filters.max_amount]);

  const isValidDateRange = useCallback((): boolean => {
    const startDate = filters.date_after;
    const endDate = filters.date_before;
    
    if (!startDate || !endDate) return true; // Si una fecha está vacía, es válido
    
    return new Date(startDate) <= new Date(endDate);
  }, [filters.date_after, filters.date_before]);

  // =====================================================
  // COMPUTED VALUES
  // =====================================================

  const memoizedActiveFilters = useMemo(() => {
    return getActiveFilters();
  }, [getActiveFilters]);

  const memoizedActiveFilterCount = useMemo(() => {
    return Object.keys(memoizedActiveFilters).length;
  }, [memoizedActiveFilters]);

  // =====================================================
  // RETURN
  // =====================================================

  return {
    // Estado de filtros
    filters,
    
    // Métodos individuales
    setType,
    setAmountRange,
    setDescription,
    setDateRange,
    setFromAccount,
    setToAccount,
    setAnyAccount,
    setBank,
    setAccountType,
    setCategory,
    setHasReference,
    setLocation,
    setTags,
    addTag,
    removeTag,
    setIsRecurring,
    setRecurringFrequency,
    setCashFlow,
    setSearch,
    
    // Operaciones en lote
    updateFilters,
    clearAllFilters,
    clearDateFilters,
    clearAmountFilters,
    clearAccountFilters,
    
    // Utilidades
    getActiveFilters,
    getActiveFilterCount,
    hasActiveFilters,
    exportFiltersAsQuery,
    
    // Presets
    applyLastWeekFilter,
    applyLastMonthFilter,
    applyThisMonthFilter,
    applyIncomeOnlyFilter,
    applyExpensesOnlyFilter,
    applyTransfersOnlyFilter,
    
    // Validaciones
    isValidAmountRange,
    isValidDateRange
  };
};

export default useTransactionFilters