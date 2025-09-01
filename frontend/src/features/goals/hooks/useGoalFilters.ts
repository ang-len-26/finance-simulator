import { useState, useCallback, useMemo, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { GoalFilters, GoalStatus, GoalType, PriorityLevel } from '../types/goals.types';

// =====================================================
// TIPOS PARA FILTROS AVANZADOS
// =====================================================
export interface GoalFilterOptions {
  status?: GoalStatus | GoalStatus[];
  goal_type?: GoalType | GoalType[];
  priority?: PriorityLevel | PriorityLevel[];
  search?: string;
  target_amount_min?: number;
  target_amount_max?: number;
  current_amount_min?: number;
  current_amount_max?: number;
  progress_min?: number;
  progress_max?: number;
  start_date?: string;
  end_date?: string;
  target_date_from?: string;
  target_date_to?: string;
  created_after?: string;
  created_before?: string;
  associated_account?: number;
  has_contributions?: boolean;
  is_overdue?: boolean;
  has_reminders?: boolean;
  is_public?: boolean;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface FilterPreset {
  name: string;
  label: string;
  filters: Partial<GoalFilterOptions>;
  icon: string;
  description: string;
}

export interface UseGoalFiltersReturn {
  // Estados principales
  filters: GoalFilterOptions;
  activeFiltersCount: number;
  isFiltering: boolean;
  
  // Acciones de filtros
  setFilter: <K extends keyof GoalFilterOptions>(key: K, value: GoalFilterOptions[K]) => void;
  setFilters: (newFilters: Partial<GoalFilterOptions>) => void;
  clearFilter: (key: keyof GoalFilterOptions) => void;
  clearAllFilters: () => void;
  resetToDefaults: () => void;
  
  // Presets
  applyPreset: (preset: FilterPreset) => void;
  presets: FilterPreset[];
  currentPreset: FilterPreset | null;
  
  // Utilidades
  getQueryString: () => string;
  getApiFilters: () => GoalFilters;
  validateDateRange: (startDate: string, endDate: string) => boolean;
  
  // Estados de validación
  errors: Record<string, string>;
  isValid: boolean;
  
  // Búsqueda avanzada
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  clearSearch: () => void;
  
  // Paginación
  page: number;
  setPage: (page: number) => void;
  pageSize: number;
  setPageSize: (size: number) => void;
}

// =====================================================
// PRESETS PREDEFINIDOS
// =====================================================
export const DEFAULT_PRESETS: FilterPreset[] = [
  {
    name: 'all_active',
    label: 'Metas Activas',
    filters: { status: 'active' },
    icon: 'target',
    description: 'Todas las metas activas'
  },
  {
    name: 'high_priority',
    label: 'Alta Prioridad',
    filters: { status: 'active', priority: 'high' },
    icon: 'alert-circle',
    description: 'Metas activas de alta prioridad'
  },
  {
    name: 'almost_complete',
    label: 'Casi Completas',
    filters: { status: 'active', progress_min: 80 },
    icon: 'trending-up',
    description: 'Metas con 80% o más de progreso'
  },
  {
    name: 'needs_attention',
    label: 'Necesitan Atención',
    filters: { status: 'active', progress_max: 25 },
    icon: 'alert-triangle',
    description: 'Metas con menos del 25% de progreso'
  },
  {
    name: 'overdue',
    label: 'Vencidas',
    filters: { is_overdue: true },
    icon: 'clock',
    description: 'Metas que pasaron su fecha límite'
  },
  {
    name: 'savings_goals',
    label: 'Ahorros',
    filters: { goal_type: 'savings', status: 'active' },
    icon: 'piggy-bank',
    description: 'Metas de ahorro activas'
  },
  {
    name: 'large_amounts',
    label: 'Montos Grandes',
    filters: { status: 'active', target_amount_min: 10000 },
    icon: 'dollar-sign',
    description: 'Metas con objetivos mayores a S/.10,000'
  },
  {
    name: 'recent',
    label: 'Recientes',
    filters: { 
      status: 'active',
      created_after: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    },
    icon: 'clock',
    description: 'Metas creadas en los últimos 30 días'
  },
  {
    name: 'completed_this_year',
    label: 'Completadas Este Año',
    filters: { 
      status: 'completed',
      created_after: `${new Date().getFullYear()}-01-01`
    },
    icon: 'check-circle',
    description: 'Metas completadas este año'
  }
];

// =====================================================
// FILTROS INICIALES
// =====================================================
const DEFAULT_FILTERS: GoalFilterOptions = {
  page: 1,
  page_size: 20,
  ordering: '-priority'
};

// =====================================================
// HOOK PRINCIPAL - useGoalFilters
// =====================================================
export const useGoalFilters = (
  initialFilters: Partial<GoalFilterOptions> = {},
  syncWithUrl = true
): UseGoalFiltersReturn => {
  
  // Estados principales
  const [filters, setFiltersState] = useState<GoalFilterOptions>({
    ...DEFAULT_FILTERS,
    ...initialFilters
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [searchParams, setSearchParams] = useSearchParams();

  // =====================================================
  // SINCRONIZACIÓN CON URL
  // =====================================================
  useEffect(() => {
    if (!syncWithUrl) return;

    // Leer filtros de la URL al montar
    const urlFilters: Partial<GoalFilterOptions> = {};
    
    // Filtros simples
    const stringParams = ['status', 'goal_type', 'priority', 'search', 'ordering'];
    stringParams.forEach(param => {
      const value = searchParams.get(param);
      if (value) {
        (urlFilters as any)[param] = value;
      }
    });

    // Filtros numéricos
    const numberParams = ['target_amount_min', 'target_amount_max', 'progress_min', 'progress_max', 'page', 'page_size', 'associated_account'];
    numberParams.forEach(param => {
      const value = searchParams.get(param);
      if (value && !isNaN(Number(value))) {
        (urlFilters as any)[param] = Number(value);
      }
    });

    // Filtros de fecha
    const dateParams = ['start_date', 'end_date', 'target_date_from', 'target_date_to', 'created_after', 'created_before'];
    dateParams.forEach(param => {
      const value = searchParams.get(param);
      if (value && isValidDate(value)) {
        (urlFilters as any)[param] = value;
      }
    });

    // Filtros booleanos
    const booleanParams = ['has_contributions', 'is_overdue', 'has_reminders', 'is_public'];
    booleanParams.forEach(param => {
      const value = searchParams.get(param);
      if (value === 'true' || value === 'false') {
        (urlFilters as any)[param] = value === 'true';
      }
    });

    if (Object.keys(urlFilters).length > 0) {
      setFiltersState(prev => ({ ...prev, ...urlFilters }));
    }
  }, [searchParams, syncWithUrl]);

  // =====================================================
  // FUNCIONES DE VALIDACIÓN
  // =====================================================
  const isValidDate = useCallback((dateString: string): boolean => {
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date.getTime());
  }, []);

  const validateDateRange = useCallback((startDate: string, endDate: string): boolean => {
    if (!isValidDate(startDate) || !isValidDate(endDate)) return false;
    return new Date(startDate) <= new Date(endDate);
  }, [isValidDate]);

  const validateFilters = useCallback((newFilters: GoalFilterOptions): Record<string, string> => {
    const newErrors: Record<string, string> = {};

    // Validar rangos de monto
    if (newFilters.target_amount_min && newFilters.target_amount_max) {
      if (newFilters.target_amount_min > newFilters.target_amount_max) {
        newErrors.target_amount = 'El monto mínimo no puede ser mayor al máximo';
      }
    }

    if (newFilters.current_amount_min && newFilters.current_amount_max) {
      if (newFilters.current_amount_min > newFilters.current_amount_max) {
        newErrors.current_amount = 'El monto actual mínimo no puede ser mayor al máximo';
      }
    }

    // Validar rangos de progreso
    if (newFilters.progress_min && newFilters.progress_min < 0) {
      newErrors.progress_min = 'El progreso mínimo no puede ser menor a 0';
    }

    if (newFilters.progress_max && newFilters.progress_max > 100) {
      newErrors.progress_max = 'El progreso máximo no puede ser mayor a 100';
    }

    if (newFilters.progress_min && newFilters.progress_max) {
      if (newFilters.progress_min > newFilters.progress_max) {
        newErrors.progress = 'El progreso mínimo no puede ser mayor al máximo';
      }
    }

    // Validar fechas
    if (newFilters.start_date && newFilters.end_date) {
      if (!validateDateRange(newFilters.start_date, newFilters.end_date)) {
        newErrors.date_range = 'La fecha de inicio debe ser anterior a la fecha final';
      }
    }

    if (newFilters.target_date_from && newFilters.target_date_to) {
      if (!validateDateRange(newFilters.target_date_from, newFilters.target_date_to)) {
        newErrors.target_date_range = 'La fecha objetivo inicial debe ser anterior a la final';
      }
    }

    if (newFilters.created_after && newFilters.created_before) {
      if (!validateDateRange(newFilters.created_after, newFilters.created_before)) {
        newErrors.created_date_range = 'La fecha de creación inicial debe ser anterior a la final';
      }
    }

    // Validar paginación
    if (newFilters.page && newFilters.page < 1) {
      newErrors.page = 'La página debe ser mayor a 0';
    }

    if (newFilters.page_size && (newFilters.page_size < 1 || newFilters.page_size > 100)) {
      newErrors.page_size = 'El tamaño de página debe estar entre 1 y 100';
    }

    return newErrors;
  }, [validateDateRange]);

  // =====================================================
  // FUNCIONES DE MANIPULACIÓN DE FILTROS
  // =====================================================
  const setFilter = useCallback(<K extends keyof GoalFilterOptions>(
    key: K, 
    value: GoalFilterOptions[K]
  ) => {
    const newFilters = { ...filters, [key]: value };
    
    // Reset página al cambiar filtros (excepto página y tamaño)
    if (key !== 'page' && key !== 'page_size') {
      newFilters.page = 1;
    }

    const validationErrors = validateFilters(newFilters);
    setErrors(validationErrors);
    
    setFiltersState(newFilters);
    
    // Sincronizar con URL
    if (syncWithUrl) {
      const newSearchParams = new URLSearchParams(searchParams);
      
      if (value !== undefined && value !== null && value !== '') {
        newSearchParams.set(key as string, String(value));
      } else {
        newSearchParams.delete(key as string);
      }
      
      setSearchParams(newSearchParams);
    }
  }, [filters, validateFilters, syncWithUrl, searchParams, setSearchParams]);

  const setFilters = useCallback((newFilters: Partial<GoalFilterOptions>) => {
    const updatedFilters = { ...filters, ...newFilters };
    
    // Reset página al cambiar múltiples filtros
    if (!('page' in newFilters)) {
      updatedFilters.page = 1;
    }

    const validationErrors = validateFilters(updatedFilters);
    setErrors(validationErrors);
    
    setFiltersState(updatedFilters);
    
    // Sincronizar con URL
    if (syncWithUrl) {
      const newSearchParams = new URLSearchParams();
      
      Object.entries(updatedFilters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          newSearchParams.set(key, String(value));
        }
      });
      
      setSearchParams(newSearchParams);
    }
  }, [filters, validateFilters, syncWithUrl, setSearchParams]);

  const clearFilter = useCallback((key: keyof GoalFilterOptions) => {
    const newFilters = { ...filters };
    delete newFilters[key];
    
    // Reset página
    newFilters.page = 1;

    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[key as string];
      return newErrors;
    });
    
    setFiltersState(newFilters);
    
    if (syncWithUrl) {
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.delete(key as string);
      setSearchParams(newSearchParams);
    }
  }, [filters, syncWithUrl, searchParams, setSearchParams]);

  const clearAllFilters = useCallback(() => {
    setFiltersState(DEFAULT_FILTERS);
    setErrors({});
    
    if (syncWithUrl) {
      setSearchParams(new URLSearchParams());
    }
  }, [syncWithUrl, setSearchParams]);

  const resetToDefaults = useCallback(() => {
    const defaultFilters = { ...DEFAULT_FILTERS, ...initialFilters };
    setFiltersState(defaultFilters);
    setErrors({});
    
    if (syncWithUrl) {
      const newSearchParams = new URLSearchParams();
      Object.entries(defaultFilters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          newSearchParams.set(key, String(value));
        }
      });
      setSearchParams(newSearchParams);
    }
  }, [initialFilters, syncWithUrl, setSearchParams]);

  // =====================================================
  // FUNCIONES DE PRESETS
  // =====================================================
  const applyPreset = useCallback((preset: FilterPreset) => {
    const presetFilters = { 
      ...DEFAULT_FILTERS,
      ...preset.filters 
    };
    
    const validationErrors = validateFilters(presetFilters);
    setErrors(validationErrors);
    
    setFiltersState(presetFilters);
    
    if (syncWithUrl) {
      const newSearchParams = new URLSearchParams();
      Object.entries(presetFilters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          newSearchParams.set(key, String(value));
        }
      });
      setSearchParams(newSearchParams);
    }
  }, [validateFilters, syncWithUrl, setSearchParams]);

  // Determinar preset actual
  const currentPreset = useMemo(() => {
    return DEFAULT_PRESETS.find(preset => {
      const presetKeys = Object.keys(preset.filters);
      const currentKeys = Object.keys(filters).filter(key => 
        filters[key as keyof GoalFilterOptions] !== undefined &&
        filters[key as keyof GoalFilterOptions] !== null &&
        filters[key as keyof GoalFilterOptions] !== ''
      );
      
      // Excluir claves de paginación y ordenamiento para comparación
      const excludeKeys = ['page', 'page_size', 'ordering'];
      const relevantCurrentKeys = currentKeys.filter(key => !excludeKeys.includes(key));
      const relevantPresetKeys = presetKeys.filter(key => !excludeKeys.includes(key));
      
      if (relevantPresetKeys.length !== relevantCurrentKeys.length) return false;
      
      return presetKeys.every(key => {
        const presetValue = preset.filters[key as keyof GoalFilterOptions];
        const currentValue = filters[key as keyof GoalFilterOptions];
        return presetValue === currentValue;
      });
    }) || null;
  }, [filters]);

  // =====================================================
  // FUNCIONES UTILITARIAS
  // =====================================================
  const getQueryString = useCallback((): string => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.set(key, String(value));
      }
    });
    
    return params.toString();
  }, [filters]);

  const getApiFilters = useCallback((): GoalFilters => {
    // Convertir filtros del hook a formato esperado por la API
    const apiFilters: GoalFilters = {};
    
    // Filtros directos
    if (filters.status) apiFilters.status = filters.status as any;
    if (filters.goal_type) apiFilters.goal_type = filters.goal_type as any;
    if (filters.priority) apiFilters.priority = filters.priority as any;
    if (filters.search) apiFilters.search = filters.search;
    if (filters.start_date) apiFilters.start_date_after = filters.start_date;
    if (filters.end_date) apiFilters.target_date_before = filters.end_date;

    return apiFilters;
  }, [filters]);

  // =====================================================
  // FUNCIONES DE BÚSQUEDA
  // =====================================================
  const setSearchTerm = useCallback((term: string) => {
    setFilter('search', term);
  }, [setFilter]);

  const clearSearch = useCallback(() => {
    clearFilter('search');
  }, [clearFilter]);

  // =====================================================
  // FUNCIONES DE PAGINACIÓN
  // =====================================================
  const setPage = useCallback((page: number) => {
    setFilter('page', page);
  }, [setFilter]);

  const setPageSize = useCallback((size: number) => {
    setFilters({ page_size: size, page: 1 });
  }, [setFilters]);

  // =====================================================
  // ESTADOS COMPUTADOS
  // =====================================================
  const activeFiltersCount = useMemo(() => {
    const excludeKeys = ['page', 'page_size', 'ordering'];
    return Object.keys(filters).filter(key => {
      if (excludeKeys.includes(key)) return false;
      const value = filters[key as keyof GoalFilterOptions];
      return value !== undefined && value !== null && value !== '';
    }).length;
  }, [filters]);

  const isFiltering = useMemo(() => activeFiltersCount > 0, [activeFiltersCount]);

  const isValid = useMemo(() => Object.keys(errors).length === 0, [errors]);

  // =====================================================
  // RETURN DEL HOOK
  // =====================================================
  return {
    // Estados principales
    filters,
    activeFiltersCount,
    isFiltering,
    
    // Acciones de filtros
    setFilter,
    setFilters,
    clearFilter,
    clearAllFilters,
    resetToDefaults,
    
    // Presets
    applyPreset,
    presets: DEFAULT_PRESETS,
    currentPreset,
    
    // Utilidades
    getQueryString,
    getApiFilters,
    validateDateRange,
    
    // Estados de validación
    errors,
    isValid,
    
    // Búsqueda avanzada
    searchTerm: filters.search || '',
    setSearchTerm,
    clearSearch,
    
    // Paginación
    page: filters.page || 1,
    setPage,
    pageSize: filters.page_size || 20,
    setPageSize,
  };
};

// =====================================================
// HOOKS ESPECIALIZADOS
// =====================================================

// Hook para filtros simples (solo activas)
export const useGoalFiltersSimple = () => {
  return useGoalFilters({ status: 'active' }, false);
};

// Hook para dashboard (con presets específicos)
export const useGoalFiltersDashboard = () => {
  const dashboardPresets: FilterPreset[] = [
    ...DEFAULT_PRESETS.slice(0, 5), // Solo los más relevantes
  ];

  const hook = useGoalFilters({}, true);
  
  return {
    ...hook,
    presets: dashboardPresets
  };
};

// Hook para vista de calendario
export const useGoalFiltersCalendar = () => {
  return useGoalFilters({
    status: 'active',
    ordering: 'target_date'
  }, true);
};

export default useGoalFilters;