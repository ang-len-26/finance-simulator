// =====================================================
// USE CATEGORIES HOOK - CORREGIDO
// Subrama 3.3.2 - Corrección de errores
// =====================================================

import { useState, useCallback, useEffect } from 'react';
import { useAsyncState } from '@/hooks/useAsyncState';
import { categoriesApi } from '../services/categoriesApi';
import {
  Category,
  CategorySummary,
  CreateCategoryData,
  UpdateCategoryData,
  CategoryFilters,
  CategoriesByType,
  CategoryHierarchy,
  CategoryTransactionsResult,
  CategoryMonthlyTrend,
  CategoryStatistics,
} from '../types/transactions.types';
import { PaginatedResponse } from '@/types/api.types';

// =====================================================
// INTERFACES
// =====================================================

export interface UseCategoriesFilters extends CategoryFilters {
  autoLoad?: boolean;
  onError?: (error: string) => void;
  onSuccess?: () => void;
}

export interface UseCategoriesReturn {
  // Estado principal
  categories: CategorySummary[];
  isLoading: boolean;
  error: string | null;
  
  // Paginación
  paginatedData: PaginatedResponse<CategorySummary> | null;
  
  // Estados específicos
  hierarchyData: CategoryHierarchy[];
  byTypeData: CategoriesByType | null;
  statisticsData: CategoryStatistics | null;
  
  // Estados de carga específicos
  isCreating: boolean;
  isUpdating: boolean;
  isDeleting: boolean;
  isLoadingHierarchy: boolean;
  
  // Acciones principales CRUD
  loadCategories: (filters?: CategoryFilters) => Promise<CategorySummary[]>;
  loadCategoriesPaginated: (filters?: CategoryFilters) => Promise<PaginatedResponse<CategorySummary>>;
  createCategory: (data: CreateCategoryData) => Promise<Category>;
  updateCategory: (id: number, data: UpdateCategoryData) => Promise<Category>;
  deleteCategory: (id: number) => Promise<boolean>;
  
  // Acciones específicas custom
  loadHierarchy: () => Promise<CategoryHierarchy[]>;
  loadByType: () => Promise<CategoriesByType>;
  loadStatistics: (startDate?: string, endDate?: string) => Promise<CategoryStatistics>;
  getCategoryTransactions: (id: number, filters?: any) => Promise<CategoryTransactionsResult>;
  getCategoryTrend: (id: number) => Promise<CategoryMonthlyTrend>;
  createDefaultCategories: () => Promise<{ message: string; total_categories: number }>;
  
  // Utilidades
  refreshCategories: () => Promise<void>;
  clearError: () => void;
  findCategoryById: (id: number) => CategorySummary | undefined;
  filterCategories: (query: string) => CategorySummary[];
  canDelete: (id: number) => Promise<{ canDelete: boolean; reason?: string }>;
}

// =====================================================
// HOOK PRINCIPAL
// =====================================================

export const useCategories = (initialFilters?: UseCategoriesFilters): UseCategoriesReturn => {
  // ERROR CORREGIDO 2: useAsyncState devuelve array, no objeto
  const [
    { data: asyncData, loading, error: asyncError }, 
    { setData, setLoading, setError, reset }
  ] = useAsyncState<PaginatedResponse<CategorySummary>>();
  
  // Estados locales
  const [categories, setCategories] = useState<CategorySummary[]>([]);
  const [paginatedData, setPaginatedData] = useState<PaginatedResponse<CategorySummary> | null>(null);
  const [hierarchyData, setHierarchyData] = useState<CategoryHierarchy[]>([]);
  const [byTypeData, setByTypeData] = useState<CategoriesByType | null>(null);
  const [statisticsData, setStatisticsData] = useState<CategoryStatistics | null>(null);
  
  // Estados de carga específicos
  const [isCreating, setIsCreating] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isLoadingHierarchy, setIsLoadingHierarchy] = useState(false);
  
  // Estado de error personalizado
  const [error, setCustomError] = useState<string | null>(null);
  
  // =====================================================
  // ACCIONES PRINCIPALES CRUD
  // =====================================================
  
  const loadCategories = useCallback(async (filters?: CategoryFilters): Promise<CategorySummary[]> => {
    try {
      setLoading(true);
      setCustomError(null);
      
      // ERROR CORREGIDO 3: Usar métodos correctos de categoriesApi
      const result = await categoriesApi.list(filters);
      setCategories(result);
      
      initialFilters?.onSuccess?.();
      return result;
    } catch (err: any) {
      const errorMessage = err.message || 'Error al cargar categorías';
      setCustomError(errorMessage);
      initialFilters?.onError?.(errorMessage);
      return [];
    } finally {
      setLoading(false);
    }
  }, [initialFilters, setLoading]);
  
  const loadCategoriesPaginated = useCallback(async (
    filters?: CategoryFilters
  ): Promise<PaginatedResponse<CategorySummary>> => {
    try {
      setLoading(true);
      setCustomError(null);
      
      const result = await categoriesApi.listPaginated(filters);
      setPaginatedData(result);
      setCategories(result.results);
      
      return result;
    } catch (err: any) {
      const errorMessage = err.message || 'Error al cargar categorías paginadas';
      setCustomError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [setLoading]);
  
  // ERROR CORREGIDO 1: Renombrar función para evitar conflicto de nombres
  const loadHierarchyData = useCallback(async (): Promise<CategoryHierarchy[]> => {
    try {
      setIsLoadingHierarchy(true);
      setCustomError(null);
      
      // ERROR CORREGIDO 3: Usar método correcto
      const result = await categoriesApi.getHierarchy();
      setHierarchyData(result);
      
      return result;
    } catch (err: any) {
      const errorMessage = err.message || 'Error al cargar jerarquía de categorías';
      setCustomError(errorMessage);
      return [];
    } finally {
      setIsLoadingHierarchy(false);
    }
  }, []);
  
  const createCategory = useCallback(async (data: CreateCategoryData): Promise<Category> => {
    try {
      setIsCreating(true);
      setCustomError(null);
      
      // Validar datos antes de enviar
      const validationErrors = categoriesApi.validateCategory(data);
      if (validationErrors.length > 0) {
        throw new Error(validationErrors.join(', '));
      }
      
      // ERROR CORREGIDO 3: Usar método correcto
      const newCategory = await categoriesApi.create(data);
      
      // Actualizar lista local
      const summary = categoriesApi.toSummary(newCategory);
      setCategories(prev => [summary, ...prev]);
      
      initialFilters?.onSuccess?.();
      return newCategory;
    } catch (err: any) {
      const errorMessage = err.message || 'Error al crear categoría';
      setCustomError(errorMessage);
      throw err;
    } finally {
      setIsCreating(false);
    }
  }, [initialFilters]);
  
  const updateCategory = useCallback(async (
    id: number, 
    data: UpdateCategoryData
  ): Promise<Category> => {
    try {
      setIsUpdating(true);
      setCustomError(null);
      
      // ERROR CORREGIDO 3: Usar método correcto
      const updatedCategory = await categoriesApi.update(id, data);
      
      // Actualizar en lista local
      const summary = categoriesApi.toSummary(updatedCategory);
      setCategories(prev => 
        prev.map(cat => cat.id === id ? summary : cat)
      );
      
      return updatedCategory;
    } catch (err: any) {
      const errorMessage = err.message || 'Error al actualizar categoría';
      setCustomError(errorMessage);
      throw err;
    } finally {
      setIsUpdating(false);
    }
  }, []);
  
  // ERROR CORREGIDO 4: Usar método correcto (delete en lugar de deleteCategory)
  const deleteCategory = useCallback(async (id: number): Promise<boolean> => {
    try {
      setIsDeleting(true);
      setCustomError(null);
      
      // Verificar si se puede eliminar
      const canDelete = await categoriesApi.canDeleteCategory(id);
      if (!canDelete.canDelete) {
        throw new Error(canDelete.reason);
      }
      
      // ERROR CORREGIDO 4: Usar método correcto
      await categoriesApi.delete(id);
      
      // Remover de lista local
      setCategories(prev => prev.filter(cat => cat.id !== id));
      
      return true;
    } catch (err: any) {
      const errorMessage = err.message || 'Error al eliminar categoría';
      setCustomError(errorMessage);
      return false;
    } finally {
      setIsDeleting(false);
    }
  }, []);
  
  // =====================================================
  // ACCIONES ESPECÍFICAS CUSTOM
  // =====================================================
  
  const loadByType = useCallback(async (): Promise<CategoriesByType> => {
    try {
      setLoading(true);
      const result = await categoriesApi.getByType();
      setByTypeData(result);
      return result;
    } catch (err: any) {
      setCustomError(err.message || 'Error al cargar categorías por tipo');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [setLoading]);
  
  const loadStatistics = useCallback(async (
    startDate?: string, 
    endDate?: string
  ): Promise<CategoryStatistics> => {
    try {
      setLoading(true);
      const result = await categoriesApi.getStatistics(startDate, endDate);
      setStatisticsData(result);
      return result;
    } catch (err: any) {
      setCustomError(err.message || 'Error al cargar estadísticas');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [setLoading]);
  
  const getCategoryTransactions = useCallback(async (
    id: number, 
    filters?: { start_date?: string; end_date?: string; limit?: number }
  ): Promise<CategoryTransactionsResult> => {
    try {
      // ERROR CORREGIDO 3: Usar método correcto
      return await categoriesApi.getTransactions(id, filters);
    } catch (err: any) {
      setCustomError(err.message || 'Error al obtener transacciones de categoría');
      throw err;
    }
  }, []);
  
  const getCategoryTrend = useCallback(async (id: number): Promise<CategoryMonthlyTrend> => {
    try {
      // ERROR CORREGIDO 3: Usar método correcto
      return await categoriesApi.getMonthlyTrend(id);
    } catch (err: any) {
      setCustomError(err.message || 'Error al obtener tendencia de categoría');
      throw err;
    }
  }, []);
  
  const createDefaultCategories = useCallback(async (): Promise<{ 
    message: string; 
    total_categories: number 
  }> => {
    try {
      setIsCreating(true);
      // ERROR CORREGIDO 3: Usar método correcto
      const result = await categoriesApi.createDefaults();
      
      // Recargar categorías después de crear defaults
      await loadCategories();
      
      return result;
    } catch (err: any) {
      setCustomError(err.message || 'Error al crear categorías predeterminadas');
      throw err;
    } finally {
      setIsCreating(false);
    }
  }, [loadCategories]);
  
  // =====================================================
  // UTILIDADES
  // =====================================================
  
  const refreshCategories = useCallback(async (): Promise<void> => {
    await loadCategories(initialFilters);
  }, [loadCategories, initialFilters]);
  
  const clearError = useCallback((): void => {
    setCustomError(null);
    reset();
  }, [reset]);
  
  const findCategoryById = useCallback((id: number): CategorySummary | undefined => {
    return categories.find(cat => cat.id === id);
  }, [categories]);
  
  const filterCategories = useCallback((query: string): CategorySummary[] => {
    if (!query.trim()) return categories;
    
    const searchQuery = query.toLowerCase();
    return categories.filter(category =>
      category.name.toLowerCase().includes(searchQuery)
    );
  }, [categories]);
  
  const canDelete = useCallback(async (
    id: number
  ): Promise<{ canDelete: boolean; reason?: string }> => {
    return await categoriesApi.canDeleteCategory(id);
  }, []);
  
  // =====================================================
  // EFECTOS
  // =====================================================
  
  // Auto-cargar categorías si se especifica
  useEffect(() => {
    if (initialFilters?.autoLoad !== false) {
      loadCategories(initialFilters);
    }
  }, [loadCategories, initialFilters]);
  
  // Auto-cargar jerarquía si se especifica
  useEffect(() => {
    if (initialFilters?.autoLoad && initialFilters.loadHierarchy) {
      loadHierarchyData();
    }
  }, [loadHierarchyData, initialFilters]);
  
  // =====================================================
  // RETURN
  // =====================================================
  
  return {
    // Estado principal
    categories,
    isLoading: loading,
    error: error || asyncError,
    
    // Paginación
    paginatedData,
    
    // Estados específicos
    hierarchyData,
    byTypeData,
    statisticsData,
    
    // Estados de carga específicos
    isCreating,
    isUpdating,
    isDeleting,
    isLoadingHierarchy,
    
    // Acciones principales CRUD
    loadCategories,
    loadCategoriesPaginated,
    createCategory,
    updateCategory,
    deleteCategory,
    
    // Acciones específicas custom
    loadHierarchy: loadHierarchyData,  // ERROR CORREGIDO 1: Usar función renombrada
    loadByType,
    loadStatistics,
    getCategoryTransactions,
    getCategoryTrend,
    createDefaultCategories,
    
    // Utilidades
    refreshCategories,
    clearError,
    findCategoryById,
    filterCategories,
    canDelete,
  };
};

// =====================================================
// HOOKS ESPECIALIZADOS
// =====================================================

/**
 * Hook para cargar solo categorías padre
 */
export const useParentCategories = () => {
  return useCategories({
    parent: null,
    autoLoad: true,
  });
};

/**
 * Hook para cargar categorías por tipo
 */
export const useCategoriesByType = (categoryType?: 'income' | 'expense' | 'both') => {
  return useCategories({
    category_type: categoryType,
    autoLoad: true,
  });
};

/**
 * Hook para cargar jerarquía completa
 */
export const useCategoryHierarchy = () => {
  const hook = useCategories({
    autoLoad: false,
    loadHierarchy: true,
  });
  
  useEffect(() => {
    hook.loadHierarchy();
  }, []);
  
  return {
    hierarchy: hook.hierarchyData,
    isLoading: hook.isLoadingHierarchy,
    error: hook.error,
    refresh: hook.loadHierarchy,
  };
};

/**
 * Hook para una categoría específica con sus transacciones
 */
export const useCategoryWithTransactions = (categoryId: number) => {
  const [category, setCategory] = useState<Category | null>(null);
  const [transactions, setTransactions] = useState<CategoryTransactionsResult | null>(null);
  const [trend, setTrend] = useState<CategoryMonthlyTrend | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const loadCategoryData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Cargar datos en paralelo
      const [categoryData, transactionsData, trendData] = await Promise.all([
        categoriesApi.get(categoryId),
        categoriesApi.getTransactions(categoryId),
        categoriesApi.getMonthlyTrend(categoryId),
      ]);
      
      setCategory(categoryData);
      setTransactions(transactionsData);
      setTrend(trendData);
    } catch (err: any) {
      setError(err.message || 'Error al cargar datos de categoría');
    } finally {
      setIsLoading(false);
    }
  }, [categoryId]);
  
  useEffect(() => {
    if (categoryId) {
      loadCategoryData();
    }
  }, [categoryId, loadCategoryData]);
  
  return {
    category,
    transactions,
    trend,
    isLoading,
    error,
    refresh: loadCategoryData,
  };
};

export default useCategories;