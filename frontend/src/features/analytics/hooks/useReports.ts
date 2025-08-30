import { useState, useCallback, useMemo } from 'react';
import { analyticsApi } from '../services/analyticsApi';
import { 
  FinancialMetric, 
  ChartData, 
  AnalyticsFilters,
  CategoryTrendData,
  FinancialRatiosData,
  AnalyticsPeriod
} from '../types/analytics.types';
import { useApi } from '@/hooks/useApi';

// =====================================================
// TIPOS ESPECÍFICOS PARA REPORTES
// =====================================================
interface ReportData {
  chart_data: ChartData;
  summary: Record<string, any>;
  metadata?: Record<string, any>;
}

interface UseReportsState {
  // Gráficos individuales
  incomeVsExpenses: ReportData | null;
  balanceTimeline: ReportData | null;
  categoryDistribution: ReportData | null;
  categoryTrends: CategoryTrendData[] | null;
  
  // Métricas financieras precalculadas
  financialMetrics: FinancialMetric[];
  
  // Ratios financieros
  financialRatios: FinancialRatiosData | null;
  
  // Estados de carga por reporte
  loading: {
    incomeVsExpenses: boolean;
    balanceTimeline: boolean;
    categoryDistribution: boolean;
    categoryTrends: boolean;
    financialMetrics: boolean;
    financialRatios: boolean;
  };
  
  // Filtros aplicados
  currentFilters: AnalyticsFilters;
  
  // Cache de datos
  cache: Map<string, { data: any; timestamp: number }>;
}

interface UseReportsOptions {
  cacheTimeout?: number; // en milisegundos
  enableCache?: boolean;
}

// =====================================================
// HOOK ESPECIALIZADO EN REPORTES
// =====================================================
export const useReports = (options: UseReportsOptions = {}) => {
  const {
    cacheTimeout = 60000, // 1 minuto
    enableCache = true
  } = options;

  // Estado principal
  const [state, setState] = useState<UseReportsState>({
    incomeVsExpenses: null,
    balanceTimeline: null,
    categoryDistribution: null,
    categoryTrends: null,
    financialMetrics: [],
    financialRatios: null,
    loading: {
      incomeVsExpenses: false,
      balanceTimeline: false,
      categoryDistribution: false,
      categoryTrends: false,
      financialMetrics: false,
      financialRatios: false
    },
    currentFilters: {},
    cache: new Map()
  });

  const [error, setError] = useState<string | null>(null);

  // Hook genérico para API calls
  const { loading: apiLoading, error: apiError } = useApi();

  // =====================================================
  // UTILIDADES DE CACHE
  // =====================================================

  /**
   * Generar clave de cache basada en filtros
   */
  const getCacheKey = useCallback((endpoint: string, filters: AnalyticsFilters): string => {
    return `${endpoint}_${JSON.stringify(filters)}`;
  }, []);

  /**
   * Obtener datos del cache si están vigentes
   */
  const getFromCache = useCallback((key: string): any | null => {
    if (!enableCache) return null;
    
    const cached = state.cache.get(key);
    if (cached && (Date.now() - cached.timestamp) < cacheTimeout) {
      return cached.data;
    }
    
    return null;
  }, [state.cache, enableCache, cacheTimeout]);

  /**
   * Guardar datos en cache
   */
  const saveToCache = useCallback((key: string, data: any): void => {
    if (!enableCache) return;
    
    setState(prev => ({
      ...prev,
      cache: new Map(prev.cache.set(key, {
        data,
        timestamp: Date.now()
      }))
    }));
  }, [enableCache]);

  // =====================================================
  // MÉTODOS DE CARGA DE REPORTES INDIVIDUALES
  // =====================================================

  /**
   * Cargar gráfico Ingresos vs Gastos
   */
  const loadIncomeVsExpenses = useCallback(async (filters: AnalyticsFilters = {}) => {
    const cacheKey = getCacheKey('income_vs_expenses', filters);
    const cached = getFromCache(cacheKey);
    
    if (cached) {
      setState(prev => ({ ...prev, incomeVsExpenses: cached }));
      return cached;
    }

    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, incomeVsExpenses: true }
    }));

    try {
      const data = await analyticsApi.getIncomeVsExpenses(filters);
      
      const reportData: ReportData = {
        chart_data: data.chart_data,
        summary: data.summary,
        metadata: {
          net_balance_data: data.net_balance_data,
          period_type: 'monthly'
        }
      };

      setState(prev => ({
        ...prev,
        incomeVsExpenses: reportData,
        currentFilters: filters,
        loading: { ...prev.loading, incomeVsExpenses: false }
      }));

      saveToCache(cacheKey, reportData);
      setError(null);
      
      return reportData;
    } catch (err: any) {
      console.error('Error loading income vs expenses:', err);
      setError(err.message || 'Error al cargar gráfico de ingresos vs gastos');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, incomeVsExpenses: false }
      }));
      throw err;
    }
  }, [getCacheKey, getFromCache, saveToCache]);

  /**
   * Cargar timeline de balance
   */
  const loadBalanceTimeline = useCallback(async (filters: AnalyticsFilters = {}) => {
    const cacheKey = getCacheKey('balance_timeline', filters);
    const cached = getFromCache(cacheKey);
    
    if (cached) {
      setState(prev => ({ ...prev, balanceTimeline: cached }));
      return cached;
    }

    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, balanceTimeline: true }
    }));

    try {
      const data = await analyticsApi.getBalanceTimeline(filters);
      
      const reportData: ReportData = {
        chart_data: data.chart_data,
        summary: data.summary
      };

      setState(prev => ({
        ...prev,
        balanceTimeline: reportData,
        currentFilters: filters,
        loading: { ...prev.loading, balanceTimeline: false }
      }));

      saveToCache(cacheKey, reportData);
      setError(null);
      
      return reportData;
    } catch (err: any) {
      console.error('Error loading balance timeline:', err);
      setError(err.message || 'Error al cargar timeline de balance');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, balanceTimeline: false }
      }));
      throw err;
    }
  }, [getCacheKey, getFromCache, saveToCache]);

  /**
   * Cargar distribución por categorías
   */
  const loadCategoryDistribution = useCallback(async (filters: AnalyticsFilters = {}) => {
    const cacheKey = getCacheKey('category_distribution', filters);
    const cached = getFromCache(cacheKey);
    
    if (cached) {
      setState(prev => ({ ...prev, categoryDistribution: cached }));
      return cached;
    }

    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, categoryDistribution: true }
    }));

    try {
      const data = await analyticsApi.getCategoryDistribution(filters);
      
      const reportData: ReportData = {
        chart_data: data.chart_data,
        summary: data.summary
      };

      setState(prev => ({
        ...prev,
        categoryDistribution: reportData,
        currentFilters: filters,
        loading: { ...prev.loading, categoryDistribution: false }
      }));

      saveToCache(cacheKey, reportData);
      setError(null);
      
      return reportData;
    } catch (err: any) {
      console.error('Error loading category distribution:', err);
      setError(err.message || 'Error al cargar distribución por categorías');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, categoryDistribution: false }
      }));
      throw err;
    }
  }, [getCacheKey, getFromCache, saveToCache]);

  /**
   * Cargar tendencias de categorías
   */
  const loadCategoryTrends = useCallback(async (filters: AnalyticsFilters = {}) => {
    const cacheKey = getCacheKey('category_trends', filters);
    const cached = getFromCache(cacheKey);
    
    if (cached) {
      setState(prev => ({ ...prev, categoryTrends: cached }));
      return cached;
    }

    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, categoryTrends: true }
    }));

    try {
      const data = await analyticsApi.getCategoryTrends(filters);
      
      setState(prev => ({
        ...prev,
        categoryTrends: data.trends,
        currentFilters: filters,
        loading: { ...prev.loading, categoryTrends: false }
      }));

      saveToCache(cacheKey, data.trends);
      setError(null);
      
      return data.trends;
    } catch (err: any) {
      console.error('Error loading category trends:', err);
      setError(err.message || 'Error al cargar tendencias de categorías');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, categoryTrends: false }
      }));
      throw err;
    }
  }, [getCacheKey, getFromCache, saveToCache]);

  /**
   * Cargar métricas financieras precalculadas
   */
  const loadFinancialMetrics = useCallback(async (filters: {
    period_type?: string;
    limit?: number;
  } = {}) => {
    const cacheKey = getCacheKey('financial_metrics', filters);
    const cached = getFromCache(cacheKey);
    
    if (cached) {
      setState(prev => ({ ...prev, financialMetrics: cached }));
      return cached;
    }

    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, financialMetrics: true }
    }));

    try {
      const data = await analyticsApi.getFinancialMetrics(filters);
      
      setState(prev => ({
        ...prev,
        financialMetrics: data.metrics,
        loading: { ...prev.loading, financialMetrics: false }
      }));

      saveToCache(cacheKey, data.metrics);
      setError(null);
      
      return data.metrics;
    } catch (err: any) {
      console.error('Error loading financial metrics:', err);
      setError(err.message || 'Error al cargar métricas financieras');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, financialMetrics: false }
      }));
      throw err;
    }
  }, [getCacheKey, getFromCache, saveToCache]);

  /**
   * Cargar ratios financieros
   */
  const loadFinancialRatios = useCallback(async (filters: AnalyticsFilters = {}) => {
    const cacheKey = getCacheKey('financial_ratios', filters);
    const cached = getFromCache(cacheKey);
    
    if (cached) {
      setState(prev => ({ ...prev, financialRatios: cached }));
      return cached;
    }

    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, financialRatios: true }
    }));

    try {
      const data = await analyticsApi.getFinancialRatios(filters);
      
      setState(prev => ({
        ...prev,
        financialRatios: data,
        currentFilters: filters,
        loading: { ...prev.loading, financialRatios: false }
      }));

      saveToCache(cacheKey, data);
      setError(null);
      
      return data;
    } catch (err: any) {
      console.error('Error loading financial ratios:', err);
      setError(err.message || 'Error al cargar ratios financieros');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, financialRatios: false }
      }));
      throw err;
    }
  }, [getCacheKey, getFromCache, saveToCache]);

  // =====================================================
  // MÉTODOS DE CARGA MÚLTIPLE
  // =====================================================

  /**
   * Cargar todos los gráficos principales
   */
  const loadAllCharts = useCallback(async (filters: AnalyticsFilters = {}) => {
    try {
      const [incomeVsExpenses, balanceTimeline, categoryDistribution] = await Promise.all([
        loadIncomeVsExpenses(filters),
        loadBalanceTimeline(filters),
        loadCategoryDistribution(filters)
      ]);

      return {
        incomeVsExpenses,
        balanceTimeline,
        categoryDistribution
      };
    } catch (err: any) {
      console.error('Error loading all charts:', err);
      throw err;
    }
  }, [loadIncomeVsExpenses, loadBalanceTimeline, loadCategoryDistribution]);

  /**
   * Cargar análisis completo
   */
  const loadCompleteAnalysis = useCallback(async (filters: AnalyticsFilters = {}) => {
    try {
      const [charts, trends, ratios, metrics] = await Promise.all([
        loadAllCharts(filters),
        loadCategoryTrends(filters),
        loadFinancialRatios(filters),
        loadFinancialMetrics({ period_type: filters.period || 'monthly' })
      ]);

      return {
        charts,
        trends,
        ratios,
        metrics
      };
    } catch (err: any) {
      console.error('Error loading complete analysis:', err);
      throw err;
    }
  }, [loadAllCharts, loadCategoryTrends, loadFinancialRatios, loadFinancialMetrics]);

  // =====================================================
  // UTILIDADES Y HELPERS
  // =====================================================

  /**
   * Limpiar cache
   */
  const clearCache = useCallback(() => {
    setState(prev => ({
      ...prev,
      cache: new Map()
    }));
  }, []);

  /**
   * Exportar datos del gráfico para Chart.js
   */
  const exportChartData = useCallback((chartType: 'incomeVsExpenses' | 'balanceTimeline' | 'categoryDistribution') => {
    const chartData = state[chartType];
    if (!chartData) return null;

    return {
      data: chartData.chart_data,
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top' as const,
          },
          title: {
            display: true,
            text: getChartTitle(chartType)
          },
        },
      },
    };
  }, [state]);

  /**
   * Obtener título del gráfico
   */
  const getChartTitle = (chartType: string): string => {
    const titles: Record<string, string> = {
      incomeVsExpenses: 'Ingresos vs Gastos',
      balanceTimeline: 'Evolución del Balance',
      categoryDistribution: 'Distribución por Categorías'
    };

    return titles[chartType] || chartType;
  };

  // =====================================================
  // COMPUTED VALUES
  // =====================================================

  const isLoadingAny = useMemo(() => {
    return Object.values(state.loading).some(loading => loading);
  }, [state.loading]);

  const hasAnyData = useMemo(() => {
    return !!(
      state.incomeVsExpenses || 
      state.balanceTimeline || 
      state.categoryDistribution ||
      state.financialMetrics.length > 0
    );
  }, [state]);

  const cacheSize = state.cache.size;

  // =====================================================
  // RETURN DEL HOOK
  // =====================================================

  return {
    // Datos de reportes
    incomeVsExpenses: state.incomeVsExpenses,
    balanceTimeline: state.balanceTimeline,
    categoryDistribution: state.categoryDistribution,
    categoryTrends: state.categoryTrends,
    financialMetrics: state.financialMetrics,
    financialRatios: state.financialRatios,
    
    // Estados
    loading: state.loading,
    isLoadingAny,
    hasAnyData,
    error: error || apiError,
    currentFilters: state.currentFilters,
    
    // Métodos de carga individuales
    loadIncomeVsExpenses,
    loadBalanceTimeline,
    loadCategoryDistribution,
    loadCategoryTrends,
    loadFinancialMetrics,
    loadFinancialRatios,
    
    // Métodos de carga múltiple
    loadAllCharts,
    loadCompleteAnalysis,
    
    // Utilidades
    exportChartData,
    clearCache,
    clearError: () => setError(null),
    
    // Info del cache
    cacheSize,
    cacheEnabled: enableCache,
  };
};

export default useReports;