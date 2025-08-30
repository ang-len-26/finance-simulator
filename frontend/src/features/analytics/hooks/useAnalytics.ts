import { useState, useEffect, useCallback } from 'react';
import analyticsApi from "../services/analyticsApi";
import { 
  FinancialMetric, 
  BudgetAlert, 
  ChartData, 
  AnalyticsFilters,
  ReportsOverview,
  TopCategory,
  RecentTransaction,
  ReportPeriod
} from '../types/analytics.types';
import { useApi } from '@/hooks/useApi';

// =====================================================
// TIPOS ESPECÍFICOS DEL HOOK
// =====================================================
interface AnalyticsState {
  // Métricas principales
  metrics: {
    total_income: number;
    total_expenses: number;
    net_balance: number;
    transaction_count: number;
    income_change: number;
    expense_change: number;
  } | null;
  
  // Datos de gráficos
  charts: {
    income_vs_expenses: ChartData | null;
    balance_timeline: ChartData | null;
    category_distribution: ChartData | null;
  };
  
  // Insights
  insights: {
    top_categories: TopCategory[],
    recent_transactions: RecentTransaction[],
    balance_summary: any;
  };
  
  // Período actual
  period: ReportPeriod | null;
  
  // Estados de carga
  loading: {
    metrics: boolean;
    charts: boolean;
    insights: boolean;
    overview: boolean;
  };
  
  // Alertas
  alerts: BudgetAlert[];
  alertsLoading: boolean;
  unreadAlertsCount: number;
}

interface UseAnalyticsOptions {
  period?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

// =====================================================
// HOOK PRINCIPAL DE ANALYTICS
// =====================================================
export const useAnalytics = (options: UseAnalyticsOptions = {}) => {
  const {
    period = 'monthly',
    autoRefresh = false,
    refreshInterval = 300000 // 5 minutos
  } = options;

  // Estados
  const [state, setState] = useState<AnalyticsState>({
    metrics: null,
    charts: {
      income_vs_expenses: null,
      balance_timeline: null,
      category_distribution: null
    },
    insights: {
      top_categories: [],
      recent_transactions: [],
      balance_summary: null
    },
    period: null,
    loading: {
      metrics: false,
      charts: false,
      insights: false,
      overview: false
    },
    alerts: [],
    alertsLoading: false,
    unreadAlertsCount: 0
  });

  const [filters, setFilters] = useState<AnalyticsFilters>({
    period
  });

  const [error, setError] = useState<string | null>(null);

  // Hook genérico para API calls
  const { loading: apiLoading, error: apiError } = useApi();

  // =====================================================
  // MÉTODOS PRINCIPALES
  // =====================================================

  /**
   * Cargar métricas principales (4 tarjetas superiores)
   */
  const loadMetrics = useCallback(async (customFilters?: AnalyticsFilters) => {
    const currentFilters = { ...filters, ...customFilters };
    
    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, metrics: true }
    }));

    try {
      const data = await analyticsApi.getMetrics(currentFilters);
      
      setState(prev => ({
        ...prev,
        metrics: data.metrics,
        period: data.period,
        loading: { ...prev.loading, metrics: false }
      }));
      
      setError(null);
    } catch (err: any) {
      console.error('Error loading metrics:', err);
      setError(err.message || 'Error al cargar métricas');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, metrics: false }
      }));
    }
  }, [filters]);

  /**
   * Cargar todos los gráficos
   */
  const loadCharts = useCallback(async (customFilters?: AnalyticsFilters) => {
    const currentFilters = { ...filters, ...customFilters };
    
    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, charts: true }
    }));

    try {
      const [incomeVsExpenses, balanceTimeline, categoryDistribution] = await Promise.all([
        analyticsApi.getIncomeVsExpenses(currentFilters),
        analyticsApi.getBalanceTimeline(currentFilters),
        analyticsApi.getCategoryDistribution(currentFilters)
      ]);

      setState(prev => ({
        ...prev,
        charts: {
          income_vs_expenses: incomeVsExpenses.chart_data,
          balance_timeline: balanceTimeline.chart_data,
          category_distribution: categoryDistribution.chart_data
        },
        loading: { ...prev.loading, charts: false }
      }));
      
      setError(null);
    } catch (err: any) {
      console.error('Error loading charts:', err);
      setError(err.message || 'Error al cargar gráficos');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, charts: false }
      }));
    }
  }, [filters]);

  /**
   * Cargar insights (categorías top, transacciones recientes)
   */
  const loadInsights = useCallback(async (customFilters?: AnalyticsFilters) => {
    const currentFilters = { ...filters, ...customFilters };
    
    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, insights: true }
    }));

    try {
      const [topCategories, recentTransactions] = await Promise.all([
        analyticsApi.getTopCategories(currentFilters),
        analyticsApi.getRecentTransactions({ limit: 5 })
      ]);

      setState(prev => ({
        ...prev,
        insights: {
          top_categories: topCategories.categories,
          recent_transactions: recentTransactions.transactions,
          balance_summary: null // Se carga con balance timeline
        },
        loading: { ...prev.loading, insights: false }
      }));
      
      setError(null);
    } catch (err: any) {
      console.error('Error loading insights:', err);
      setError(err.message || 'Error al cargar insights');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, insights: false }
      }));
    }
  }, [filters]);

  /**
   * Cargar dashboard completo en una sola llamada
   */
  const loadReportsOverview = useCallback(async (customFilters?: AnalyticsFilters) => {
    const currentFilters = { ...filters, ...customFilters };
    
    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, overview: true }
    }));

    try {
      const overview = await analyticsApi.getReportsOverview(currentFilters);
      
      setState(prev => ({
        ...prev,
        metrics: overview.metrics,
        charts: overview.charts,
        insights: overview.insights,
        period: overview.period,
        loading: { ...prev.loading, overview: false }
      }));
      
      setError(null);
    } catch (err: any) {
      console.error('Error loading reports overview:', err);
      setError(err.message || 'Error al cargar dashboard completo');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, overview: false }
      }));
    }
  }, [filters]);

  /**
   * Cargar alertas de presupuesto
   */
  const loadAlerts = useCallback(async (alertFilters?: {
    severity?: string;
    alert_type?: string;
    is_read?: boolean;
  }) => {
    setState(prev => ({
      ...prev,
      alertsLoading: true
    }));

    try {
      const alertsData = await analyticsApi.getAlerts(alertFilters);
      
      setState(prev => ({
        ...prev,
        alerts: alertsData.alerts,
        unreadAlertsCount: alertsData.summary.unread_count,
        alertsLoading: false
      }));
      
      setError(null);
    } catch (err: any) {
      console.error('Error loading alerts:', err);
      setError(err.message || 'Error al cargar alertas');
      setState(prev => ({
        ...prev,
        alertsLoading: false
      }));
    }
  }, []);

  /**
   * Marcar alertas como leídas
   */
  const markAlertsAsRead = useCallback(async (alertIds: number[]) => {
    try {
      await analyticsApi.markAlertsAsRead(alertIds);
      
      // Actualizar estado local
      setState(prev => ({
        ...prev,
        alerts: prev.alerts.map(alert => 
          alertIds.includes(alert.id) 
            ? { ...alert, is_read: true }
            : alert
        ),
        unreadAlertsCount: Math.max(0, prev.unreadAlertsCount - alertIds.length)
      }));
      
      setError(null);
    } catch (err: any) {
      console.error('Error marking alerts as read:', err);
      setError(err.message || 'Error al marcar alertas como leídas');
    }
  }, []);

  // =====================================================
  // MÉTODOS DE FILTRADO Y ACTUALIZACIÓN
  // =====================================================

  /**
   * Actualizar filtros y recargar datos
   */
  const updateFilters = useCallback(async (newFilters: Partial<AnalyticsFilters>) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    
    // Recargar datos con nuevos filtros
    await loadReportsOverview(updatedFilters);
  }, [filters, loadReportsOverview]);

  /**
   * Cambiar período y recargar
   */
  const changePeriod = useCallback(async (newPeriod: string) => {
    await updateFilters({ period: newPeriod });
  }, [updateFilters]);

  /**
   * Refrescar todos los datos
   */
  const refreshAll = useCallback(async () => {
    await Promise.all([
      loadReportsOverview(),
      loadAlerts()
    ]);
  }, [loadReportsOverview, loadAlerts]);

  /**
   * Refrescar solo métricas (más rápido)
   */
  const refreshMetrics = useCallback(async () => {
    await loadMetrics();
  }, [loadMetrics]);

  // =====================================================
  // EFECTOS Y AUTO-REFRESH
  // =====================================================

  // Cargar datos iniciales
  useEffect(() => {
    loadReportsOverview();
    loadAlerts();
  }, []);

  // Auto-refresh si está habilitado
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      refreshMetrics(); // Solo métricas para no sobrecargar
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, refreshMetrics]);

  // =====================================================
  // COMPUTED PROPERTIES
  // =====================================================

  const isLoading = state.loading.overview || state.loading.metrics || state.loading.charts || state.loading.insights;
  const hasData = state.metrics !== null;
  const hasAlerts = state.alerts.length > 0;
  const hasUnreadAlerts = state.unreadAlertsCount > 0;

  // Métricas calculadas
  const savingsRate = state.metrics ? 
    state.metrics.total_income > 0 
      ? ((state.metrics.total_income - state.metrics.total_expenses) / state.metrics.total_income * 100)
      : 0 
    : 0;

  const expenseRatio = state.metrics ?
    state.metrics.total_income > 0
      ? (state.metrics.total_expenses / state.metrics.total_income * 100)
      : 0
    : 0;

  // =====================================================
  // RETURN DEL HOOK
  // =====================================================

  return {
    // Estado principal
    ...state,
    
    // Estados computados
    isLoading,
    hasData,
    hasAlerts,
    hasUnreadAlerts,
    savingsRate: Math.round(savingsRate * 100) / 100,
    expenseRatio: Math.round(expenseRatio * 100) / 100,
    
    // Filtros actuales
    filters,
    
    // Error handling
    error: error || apiError,
    
    // Métodos de carga
    loadMetrics,
    loadCharts,
    loadInsights,
    loadReportsOverview,
    loadAlerts,
    
    // Métodos de actualización
    updateFilters,
    changePeriod,
    refreshAll,
    refreshMetrics,
    markAlertsAsRead,
    
    // Utilidades
    clearError: () => setError(null),
  };
};

export default useAnalytics;