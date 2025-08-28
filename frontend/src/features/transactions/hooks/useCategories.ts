// =====================================================
// useCategories - Hook para gestión de categorías
// Basado en CategoryViewSet del backend
// Subrama 3.2 - Transactions Hooks
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
  CategoryStatistics 
} from '../types/transactions.types';
import { PaginatedResponse, ApiError } from '@/types/api.types';

// =====================================================
// TIPOS INTERNOS DEL HOOK
// =====================================================

interface UseCategoriesState {
  categories: CategorySummary[];
  selectedCategory: Category | null;
  hierarchyCategories: CategoryHierarchy[];
  categoriesByType: CategoriesByType | null;
  totalCount: number;
}

interface UseCategoriesOptions {
  initialFilters?: CategoryFilters;
  autoLoad?: boolean;
  loadHierarchy?: boolean;
}

interface UseCategoriesReturn {
  // Estado principal
  data: UseCategoriesState;
  isLoading: boolean;
  error: ApiError | null;
  
  // Operaciones CRUD
  loadCategories: (filters?: CategoryFilters) => Promise<void>;
  createCategory: (data: CreateCategoryData) => Promise<Category>;
  updateCategory: (id: number, data: UpdateCategoryData) => Promise<Category>;
  deleteCategory: (id: number) => Promise<void>;
  getCategory: (id: number) => Promise<Category>;
  
  // Operaciones especiales
  loadCategoriesByType: () => Promise<CategoriesByType>;
  loadHierarchy: () => Promise<CategoryHierarchy[]>;
  getCategoryTransactions: (id: number, startDate?: string, endDate?: string, limit?: number) => Promise<CategoryTransactionsResult>;
  getCategoryTrend: (id: number) => Promise<CategoryMonthlyTrend>;
  getCategoryStatistics: (startDate?: string, endDate?: string) => Promise<CategoryStatistics>;
  createDefaultCategories: () => Promise<{ message: string; total_categories: number }>;
  
  // Utilidades
  refreshCategories: () => Promise<void>;
  clearError: () => void;
  setSelectedCategory: (category: Category | null) => void;
  
  // Helpers específicos de categorías
  getCategoryById: (id: number) => CategorySummary | null;
  getSubcategories: (parentId: number) => CategorySummary[];
  getParentCategories: () => CategorySummary[];
  filterCategoriesByType: (type: 'income' | 'expense' | 'both') => CategorySummary[];
}

// =====================================================
// HOOK PRINCIPAL
// =====================================================

export const useCategories = (options: UseCategoriesOptions = {}): UseCategoriesReturn => {
  const {
    initialFilters = { is_active: true },
    autoLoad = true,
    loadHierarchy = false
  } = options;

  // Estado principal usando useAsyncState
  const {
    data: asyncData,
    isLoading,
    error,
    execute,
    clearError
  } = useAsyncState<PaginatedResponse<CategorySummary>>();

  // Estado local del hook
  const [state, setState] = useState<UseCategoriesState>({
    categories: [],
    selectedCategory: null,
    hierarchyCategories: [],
    categoriesByType: null,
    totalCount: 0
  });

  // Filtros actuales
  const [currentFilters, setCurrentFilters] = useState<CategoryFilters>(initialFilters);

  // =====================================================
  // OPERACIONES DE CARGA
  // =====================================================

  const loadCategories = useCallback(async (filters?: CategoryFilters) => {
    const finalFilters = filters ? { ...currentFilters, ...filters } : currentFilters;
    setCurrentFilters(finalFilters);

    const result = await execute(() => categoriesApi.getCategories(finalFilters));
    
    if (result) {
      setState(prev => ({
        ...prev,
        categories: result.results,
        totalCount: result.count
      }));
    }
  }, [currentFilters, execute]);

  const loadCategoriesByType = useCallback(async (): Promise<CategoriesByType> => {
    const result = await categoriesApi.getCategoriesByType();
    
    setState(prev => ({
      ...prev,
      categoriesByType: result
    }));

    return result;
  }, []);

  const loadHierarchy = useCallback(async (): Promise<CategoryHierarchy[]> => {
    const result = await categoriesApi.getCategoryHierarchy();
    
    setState(prev => ({
      ...prev,
      hierarchyCategories: result
    }));

    return result;
  }, []);

  // =====================================================
  // OPERACIONES CRUD
  // =====================================================

  const createCategory = useCallback(async (data: CreateCategoryData): Promise<Category> => {
    const newCategory = await categoriesApi.createCategory(data);
    
    // Agregar a la lista local
    const categorySummary: CategorySummary = {
      id: newCategory.id,
      name: newCategory.name,
      icon: newCategory.icon,
      color: newCategory.color,
      category_type: newCategory.category_type
    };

    setState(prev => ({
      ...prev,
      categories: [categorySummary, ...prev.categories],
      totalCount: prev.totalCount + 1
    }));

    return newCategory;
  }, []);

  const updateCategory = useCallback(async (id: number, data: UpdateCategoryData): Promise<Category> => {
    const updatedCategory = await categoriesApi.updateCategory(id, data);
    
    // Actualizar en la lista local
    setState(prev => ({
      ...prev,
      categories: prev.categories.map(c => 
        c.id === id 
          ? {
              ...c,
              name: updatedCategory.name,
              icon: updatedCategory.icon,
              color: updatedCategory.color,
              category_type: updatedCategory.category_type
            }
          : c
      ),
      selectedCategory: prev.selectedCategory?.id === id ? updatedCategory : prev.selectedCategory
    }));

    return updatedCategory;
  }, []);

  const deleteCategory = useCallback(async (id: number): Promise<void> => {
    await categoriesApi.deleteCategory(id);
    
    // Remover de la lista local
    setState(prev => ({
      ...prev,
      categories: prev.categories.filter(c => c.id !== id),
      totalCount: Math.max(0, prev.totalCount - 1),
      selectedCategory: prev.selectedCategory?.id === id ? null : prev.selectedCategory
    }));
  }, []);

  const getCategory = useCallback(async (id: number): Promise<Category> => {
    const category = await categoriesApi.getCategory(id);
    
    setState(prev => ({
      ...prev,
      selectedCategory: category
    }));

    return category;
  }, []);

  // =====================================================
  // OPERACIONES ESPECIALES
  // =====================================================

  const getCategoryTransactions = useCallback(async (
    id: number, 
    startDate?: string, 
    endDate?: string, 
    limit?: number
  ): Promise<CategoryTransactionsResult> => {
    return await categoriesApi.getCategoryTransactions(id, { 
      start_date: startDate, 
      end_date: endDate, 
      limit 
    });
  }, []);

  const getCategoryTrend = useCallback(async (id: number): Promise<CategoryMonthlyTrend> => {
    return await categoriesApi.getCategoryTrend(id);
  }, []);

  const getCategoryStatistics = useCallback(async (startDate?: string, endDate?: string): Promise<CategoryStatistics> => {
    return await categoriesApi.getCategoryStatistics({ 
      start_date: startDate, 
      end_date: endDate 
    });
  }, []);

  const createDefaultCategories = useCallback(async (): Promise<{ message: string; total_categories: number }> => {
    const result = await categoriesApi.createDefaultCategories();
    
    // Recargar categorías después de crear las predeterminadas
    await loadCategories();
    
    return result;
  }, [loadCategories]);

  // =====================================================
  // HELPERS ESPECÍFICOS
  // =====================================================

  const getCategoryById = useCallback((id: number): CategorySummary | null => {
    return state.categories.find(c => c.id === id) || null;
  }, [state.categories]);

  const getSubcategories = useCallback((parentId: number): CategorySummary[] => {
    // Esta función requiere datos de jerarquía cargados
    const parentCategory = state.hierarchyCategories.find(c => c.id === parentId);
    return parentCategory?.subcategories || [];
  }, [state.hierarchyCategories]);

  const getParentCategories = useCallback((): CategorySummary[] => {
    // Categorías sin parent (categorías padre)
    return state.categories.filter(c => 
      !state.categories.some(parent => 
        parent.id !== c.id // Evitar auto-referencia
      )
    );
  }, [state.categories]);

  const filterCategoriesByType = useCallback((type: 'income' | 'expense' | 'both'): CategorySummary[] => {
    return state.categories.filter(c => 
      c.category_type === type || c.category_type === 'both'
    );
  }, [state.categories]);

  // =====================================================
  // UTILIDADES
  // =====================================================

  const refreshCategories = useCallback(async () => {
    await loadCategories(currentFilters);
    if (loadHierarchy) {
      await loadHierarchy();
    }
  }, [loadCategories, currentFilters, loadHierarchy]);

  const setSelectedCategory = useCallback((category: Category | null) => {
    setState(prev => ({
      ...prev,
      selectedCategory: category
    }));
  }, []);

  // =====================================================
  // EFECTOS
  // =====================================================

  useEffect(() => {
    if (autoLoad) {
      loadCategories();
    }
  }, [autoLoad]);

  useEffect(() => {
    if (loadHierarchy && autoLoad) {
      loadHierarchy();
    }
  }, [loadHierarchy, autoLoad]);

  // =====================================================
  // RETURN
  // =====================================================

  return {
    // Estado
    data: state,
    isLoading,
    error,
    
    // CRUD
    loadCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    getCategory,
    
    // Especiales
    loadCategoriesByType,
    loadHierarchy,
    getCategoryTransactions,
    getCategoryTrend,
    getCategoryStatistics,
    createDefaultCategories,
    
    // Utilidades
    refreshCategories,
    clearError,
    setSelectedCategory,
    
    // Helpers
    getCategoryById,
    getSubcategories,
    getParentCategories,
    filterCategoriesByType
  };
};

export default useCategories;