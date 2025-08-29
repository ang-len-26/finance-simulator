// =====================================================
// CATEGORIES API SERVICE
// Basado en CategoryViewSet del backend
// Rama 3.1 - Transactions Module
// =====================================================

import apiClient from '@/services/api/client';
import { TRANSACTIONS_ENDPOINTS, buildUrlWithParams, buildCategoryFilters } from '@/services/api/endpoints';
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
// CATEGORIES CRUD API
// =====================================================

export const categoriesApi = {
  // ✅ CRUD básico
  list: async (filters?: CategoryFilters): Promise<CategorySummary[]> => {
    const cleanFilters = filters ? buildCategoryFilters(filters) : {};
    const url = buildUrlWithParams(TRANSACTIONS_ENDPOINTS.CATEGORIES, cleanFilters);
    return await apiClient.get<CategorySummary[]>(url);
  },

  listPaginated: async (filters?: CategoryFilters): Promise<PaginatedResponse<CategorySummary>> => {
    const cleanFilters = filters ? { ...buildCategoryFilters(filters), paginated: true } : { paginated: true };
    const url = buildUrlWithParams(TRANSACTIONS_ENDPOINTS.CATEGORIES, cleanFilters);
    return await apiClient.get<PaginatedResponse<CategorySummary>>(url);
  },

  create: async (data: CreateCategoryData): Promise<Category> => {
    return await apiClient.post<Category>(TRANSACTIONS_ENDPOINTS.CATEGORIES, data);
  },

  get: async (id: number): Promise<Category> => {
    return await apiClient.get<Category>(TRANSACTIONS_ENDPOINTS.CATEGORY_DETAIL(id));
  },

  update: async (id: number, data: UpdateCategoryData): Promise<Category> => {
    return await apiClient.put<Category>(TRANSACTIONS_ENDPOINTS.CATEGORY_DETAIL(id), data);
  },

  partialUpdate: async (id: number, data: Partial<UpdateCategoryData>): Promise<Category> => {
    return await apiClient.patch<Category>(TRANSACTIONS_ENDPOINTS.CATEGORY_DETAIL(id), data);
  },

  delete: async (id: number): Promise<void> => {
    return await apiClient.delete<void>(TRANSACTIONS_ENDPOINTS.CATEGORY_DETAIL(id));
  },

  // ✅ Custom actions - basados en @action del CategoryViewSet
  getByType: async (): Promise<CategoriesByType> => {
    return await apiClient.get<CategoriesByType>(TRANSACTIONS_ENDPOINTS.CATEGORIES_BY_TYPE);
  },

  getHierarchy: async (): Promise<CategoryHierarchy[]> => {
    return await apiClient.get<CategoryHierarchy[]>(TRANSACTIONS_ENDPOINTS.CATEGORIES_HIERARCHY);
  },

  getTransactions: async (
    id: number, 
    filters?: { start_date?: string; end_date?: string; limit?: number }
  ): Promise<CategoryTransactionsResult> => {
    const params = filters || {};
    const url = buildUrlWithParams(TRANSACTIONS_ENDPOINTS.CATEGORY_TRANSACTIONS(id), params);
    return await apiClient.get<CategoryTransactionsResult>(url);
  },

  getMonthlyTrend: async (id: number): Promise<CategoryMonthlyTrend> => {
    return await apiClient.get<CategoryMonthlyTrend>(TRANSACTIONS_ENDPOINTS.CATEGORY_MONTHLY_TREND(id));
  },

  createDefaults: async (): Promise<{ message: string; total_categories: number }> => {
    return await apiClient.post<{ message: string; total_categories: number }>(
      TRANSACTIONS_ENDPOINTS.CATEGORIES_CREATE_DEFAULTS
    );
  },

  getStatistics: async (
    startDate?: string, 
    endDate?: string
  ): Promise<CategoryStatistics> => {
    const params: Record<string, any> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const url = buildUrlWithParams(TRANSACTIONS_ENDPOINTS.CATEGORIES_STATISTICS, params);
    return await apiClient.get<CategoryStatistics>(url);
  },

  getSummaryReport: async (
    periodType: 'monthly' | 'weekly' | 'daily' = 'monthly',
    startDate?: string,
    endDate?: string
  ): Promise<any> => { // CategorySummaryReport type would come from analytics
    const params: Record<string, any> = { period_type: periodType };
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const url = buildUrlWithParams(TRANSACTIONS_ENDPOINTS.CATEGORIES_SUMMARY_REPORT, params);
    return await apiClient.get<any>(url);
  },

  // ✅ Utility functions
  validateCategory: (data: CreateCategoryData): string[] => {
    const errors: string[] = [];
    
    if (!data.name?.trim()) {
      errors.push('El nombre de la categoría es requerido');
    }
    
    if (data.name && data.name.length > 100) {
      errors.push('El nombre no puede exceder 100 caracteres');
    }
    
    if (!data.category_type) {
      errors.push('El tipo de categoría es requerido');
    }
    
    if (data.color && !data.color.match(/^#[0-9A-Fa-f]{6}$/)) {
      errors.push('El color debe estar en formato hexadecimal (#ffffff)');
    }
    
    return errors;
  },

  // ✅ Helper functions para UI
  getParentCategories: async (): Promise<CategorySummary[]> => {
    return await categoriesApi.list({ parent: null });
  },

  getSubcategories: async (parentId: number): Promise<CategorySummary[]> => {
    return await categoriesApi.list({ parent: parentId });
  },

  getActiveCategories: async (): Promise<CategorySummary[]> => {
    return await categoriesApi.list({ is_active: true });
  },

  getIncomeCategories: async (): Promise<CategorySummary[]> => {
    const byType = await categoriesApi.getByType();
    return byType.income;
  },

  getExpenseCategories: async (): Promise<CategorySummary[]> => {
    const byType = await categoriesApi.getByType();
    return byType.expense;
  },

  // ✅ Búsqueda y filtrado
  searchCategories: async (query: string): Promise<CategorySummary[]> => {
    const categories = await categoriesApi.list();
    return categories.filter(category => 
      category.name.toLowerCase().includes(query.toLowerCase())
    );
  },

  // ✅ Operaciones en lote
  bulkCreate: async (categories: CreateCategoryData[]): Promise<Category[]> => {
    const promises = categories.map(category => categoriesApi.create(category));
    return await Promise.all(promises);
  },

  bulkDelete: async (ids: number[]): Promise<void> => {
    const promises = ids.map(id => categoriesApi.delete(id));
    await Promise.all(promises);
  },

  bulkUpdateStatus: async (ids: number[], isActive: boolean): Promise<void> => {
    const promises = ids.map(id => 
      categoriesApi.partialUpdate(id, { is_active: isActive })
    );
    await Promise.all(promises);
  },

  // ✅ Análisis y reportes
  getTopCategoriesByUsage: async (
    limit: number = 5,
    startDate?: string,
    endDate?: string
  ): Promise<CategorySummary[]> => {
    const stats = await categoriesApi.getStatistics(startDate, endDate);
    return stats.most_used_categories
      .slice(0, limit)
      .map(cat => ({
        id: 0, // Mock ID since statistics doesn't provide it
        name: cat.name,
        icon: cat.icon,
        color: cat.color,
        category_type: cat.type
      }));
  },

  getCategoryUsagePercentage: async (
    categoryId: number,
    startDate?: string,
    endDate?: string
  ): Promise<number> => {
    const stats = await categoriesApi.getStatistics(startDate, endDate);
    const category = stats.most_used_categories.find(cat => cat.name);
    
    if (!category) return 0;
    
    const totalAmount = stats.most_used_categories.reduce(
      (sum, cat) => sum + cat.total_amount, 
      0
    );
    
    return totalAmount > 0 ? (category.total_amount / totalAmount) * 100 : 0;
  },

  // ✅ Validación de jerarquías
  canDeleteCategory: async (id: number): Promise<{ canDelete: boolean; reason?: string }> => {
    try {
      const category = await categoriesApi.get(id);
      
      // Verificar si tiene subcategorías
      if (category.subcategories && category.subcategories.length > 0) {
        return {
          canDelete: false,
          reason: `Esta categoría tiene ${category.subcategories.length} subcategorías. Elimínalas primero.`
        };
      }
      
      // Verificar si tiene transacciones
      if (category.transaction_count > 0) {
        return {
          canDelete: false,
          reason: `Esta categoría tiene ${category.transaction_count} transacciones asociadas.`
        };
      }
      
      return { canDelete: true };
    } catch (error) {
      return {
        canDelete: false,
        reason: 'Error al verificar la categoría'
      };
    }
  },

  // ✅ Formateo y utilidades
  formatCategoryName: (category: CategorySummary | Category): string => {
    if ('parent_name' in category && category.parent_name) {
      return `${category.parent_name} > ${category.name}`;
    }
    return category.name;
  },

  getCategoryIcon: (category: CategorySummary | Category): string => {
    return category.icon || 'Receipt';
  },

  getCategoryColor: (category: CategorySummary | Category): string => {
    return category.color || '#6366f1';
  },

  // ✅ Conversión de datos
  toSummary: (category: Category): CategorySummary => ({
    id: category.id,
    name: category.name,
    icon: category.icon,
    color: category.color,
    category_type: category.category_type
  })
};