import { useState, useCallback, useEffect, useMemo } from 'react';
import analyticsApi from '../services/analyticsApi';
import { 
  FinancialMetric, 
  FinancialRatios,
  AnalyticsFilters,
  MetricsComparison,
  PeriodType
} from '../types/analytics.types';
import { useApi } from '@/hooks/useApi';

// =====================================================
// TIPOS ESPECÍFICOS PARA MÉTRICAS
// =====================================================
interface MetricsSummary {
  total_income: number;
  total_expenses: number;
  net_balance: number;
  transaction_count: number;
  income_change: number;
  expense_change: number;
}

interface FinancialHealth {
  score: number; // 0-100
  level: 'poor' | 'fair' | 'good' | 'excellent';
  factors: {
    savings_rate: { value: number; weight: number; score: number };
    expense_ratio: { value: number; weight: number; score: number };
    income_stability: { value: number; weight: number; score: number };
    debt_ratio: { value: number; weight: number; score: number };
  };
  recommendations: string[];
}

interface UseFinancialMetricsState {
  // Métricas actuales
  currentMetrics: MetricsSummary | null;
  previousMetrics: MetricsSummary | null;
  
  // Histórico de métricas
  metricsHistory: FinancialMetric[];
  
  // Ratios financieros
  ratios: FinancialRatios | null;
  
  // Comparativas y tendencias
  comparison: MetricsComparison | null;
  trends: {
    income: { direction: 'up' | 'down' | 'stable'; percentage: number };
    expenses: { direction: 'up' | 'down' | 'stable'; percentage: number };
    balance: { direction: 'up' | 'down' | 'stable'; percentage: number };
  } | null;
  
  // Salud financiera calculada
  financialHealth: FinancialHealth | null;
  
  // Período actual
  currentPeriod: FinancialMetric | null;
  
  // Estados de carga
  loading: {
    metrics: boolean;
    history: boolean;
    ratios: boolean;
    health: boolean;
  };
  
  // Configuración
  periodType: PeriodType;
  autoUpdate: boolean;
}

interface UseFinancialMetricsOptions {
  periodType?: PeriodType;
  autoUpdate?: boolean;
  updateInterval?: number;
  includeProjections?: boolean;
}

// =====================================================
// HOOK ESPECIALIZADO EN MÉTRICAS FINANCIERAS
// =====================================================
export const useFinancialMetrics = (options: UseFinancialMetricsOptions = {}) => {
  const {
    periodType = 'monthly',
    autoUpdate = true,
    updateInterval = 300000, // 5 minutos
    includeProjections = false
  } = options;

  // Estado principal
  const [state, setState] = useState<UseFinancialMetricsState>({
    currentMetrics: null,
    previousMetrics: null,
    metricsHistory: [],
    ratios: null,
    comparison: null,
    trends: null,
    financialHealth: null,
    currentPeriod: null,
    loading: {
      metrics: false,
      history: false,
      ratios: false,
      health: false
    },
    periodType,
    autoUpdate
  });

  const [error, setError] = useState<string | null>(null);

  // Hook genérico para API calls
  const { loading: apiLoading, error: apiError } = useApi(async () => {});

  // =====================================================
  // MÉTODOS DE ANÁLISIS Y COMPARACIÓN
  // =====================================================

  /**
   * Calcular tendencias basadas en el historial
   */
  const calculateTrends = useCallback((): typeof state.trends => {
    if (state.metricsHistory.length < 2) return null;

    const recent = state.metricsHistory[0];
    const previous = state.metricsHistory[1];

    const calculateTrend = (current: number, prev: number) => {
      const change = ((current - prev) / Math.abs(prev)) * 100;
      return {
        direction: change > 5 ? 'up' as const : change < -5 ? 'down' as const : 'stable' as const,
        percentage: Math.abs(change)
      };
    };

    return {
      income: calculateTrend(parseFloat(recent.total_income), parseFloat(previous.total_income)),
      expenses: calculateTrend(parseFloat(recent.total_expenses), parseFloat(previous.total_expenses)),
      balance: calculateTrend(parseFloat(recent.net_balance), parseFloat(previous.net_balance))
    };
  }, [state.metricsHistory]);

  /**
   * Obtener comparación detallada con período anterior
   */
  const getDetailedComparison = useCallback((): MetricsComparison | null => {
    if (!state.comparison) return null;
    return state.comparison;
  }, [state.comparison]);

  // =====================================================
  // MÉTODOS DE PROYECCIÓN (OPCIONAL)
  // =====================================================

  /**
   * Proyectar métricas futuras basadas en tendencias
   */
  const projectFutureMetrics = useCallback((months: number = 3) => {
    if (!includeProjections || !state.currentMetrics || state.metricsHistory.length < 3) {
      return null;
    }

    try {
      // Calcular tendencias de los últimos 3 meses
      const recentHistory = state.metricsHistory.slice(0, 3);
      const incomeGrowthRate = calculateGrowthRate(
        recentHistory.map(m => parseFloat(m.total_income))
      );
      const expenseGrowthRate = calculateGrowthRate(
        recentHistory.map(m => parseFloat(m.total_expenses))
      );

      // Proyectar valores futuros
      const projections = [];
      let currentIncome = state.currentMetrics.total_income;
      let currentExpenses = state.currentMetrics.total_expenses;

      for (let i = 1; i <= months; i++) {
        currentIncome *= (1 + incomeGrowthRate);
        currentExpenses *= (1 + expenseGrowthRate);

        projections.push({
          month: i,
          projected_income: Math.round(currentIncome * 100) / 100,
          projected_expenses: Math.round(currentExpenses * 100) / 100,
          projected_balance: Math.round((currentIncome - currentExpenses) * 100) / 100
        });
      }

      return projections;
    } catch (err) {
      console.error('Error calculating projections:', err);
      return null;
    }
  }, [includeProjections, state.currentMetrics, state.metricsHistory]);

  const calculateGrowthRate = (values: number[]): number => {
    if (values.length < 2) return 0;
    
    const growthRates = [];
    for (let i = 1; i < values.length; i++) {
      if (values[i - 1] !== 0) {
        growthRates.push((values[i] - values[i - 1]) / Math.abs(values[i - 1]));
      }
    }
    
    return growthRates.length > 0 
      ? growthRates.reduce((sum, rate) => sum + rate, 0) / growthRates.length 
      : 0;
  };

  // =====================================================
  // MÉTODOS PRINCIPALES DE ACTUALIZACIÓN
  // =====================================================

  /**
   * Cargar todos los datos de métricas
   */
  const loadAllMetrics = useCallback(async (filters: AnalyticsFilters = {}) => {
    try {
      const [currentMetrics, history, ratios] = await Promise.all([
        loadCurrentMetrics(filters),
        loadMetricsHistory(),
        loadFinancialRatios(filters)
      ]);

      // Calcular tendencias después de cargar datos
      const trends = calculateTrends();
      
      setState(prev => ({
        ...prev,
        trends
      }));

      // Calcular salud financiera
      await calculateFinancialHealth();

      return { currentMetrics, history, ratios };
    } catch (err: any) {
      console.error('Error loading all metrics:', err);
      throw err;
    }
  }, [loadCurrentMetrics, loadMetricsHistory, loadFinancialRatios, calculateTrends, calculateFinancialHealth]);

  /**
   * Refrescar solo métricas críticas
   */
  const refreshCriticalMetrics = useCallback(async () => {
    try {
      await loadCurrentMetrics();
      await loadFinancialRatios();
      await calculateFinancialHealth();
    } catch (err: any) {
      console.error('Error refreshing critical metrics:', err);
    }
  }, [loadCurrentMetrics, loadFinancialRatios, calculateFinancialHealth]);

  /**
   * Cambiar período de análisis
   */
  const changePeriodType = useCallback(async (newPeriodType: PeriodType) => {
    setState(prev => ({
      ...prev,
      periodType: newPeriodType
    }));

    // Recargar datos con nuevo período
    await loadAllMetrics();
  }, [loadAllMetrics]);

  // =====================================================
  // EFECTOS Y AUTO-UPDATE
  // =====================================================

  // Cargar datos iniciales
  useEffect(() => {
    loadAllMetrics();
  }, []);

  // Auto-update si está habilitado
  useEffect(() => {
    if (!autoUpdate) return;

    const interval = setInterval(() => {
      refreshCriticalMetrics();
    }, updateInterval);

    return () => clearInterval(interval);
  }, [autoUpdate, updateInterval, refreshCriticalMetrics]);

  // Actualizar tendencias cuando cambie el historial
  useEffect(() => {
    if (state.metricsHistory.length >= 2) {
      const trends = calculateTrends();
      setState(prev => ({ ...prev, trends }));
    }
  }, [state.metricsHistory, calculateTrends]);

  // =====================================================
  // COMPUTED VALUES
  // =====================================================

  const isLoadingAny = useMemo(() => {
    return Object.values(state.loading).some(loading => loading);
  }, [state.loading]);

  const hasCompleteData = useMemo(() => {
    return !!(
      state.currentMetrics && 
      state.ratios && 
      state.metricsHistory.length > 0
    );
  }, [state]);

  const healthColor = useMemo(() => {
    if (!state.financialHealth) return 'gray';
    
    const colors = {
      excellent: 'green',
      good: 'blue', 
      fair: 'yellow',
      poor: 'red'
    };
    
    return colors[state.financialHealth.level];
  }, [state.financialHealth]);

  // =====================================================
  // RETURN DEL HOOK
  // =====================================================

  return {
    // Datos principales
    currentMetrics: state.currentMetrics,
    previousMetrics: state.previousMetrics,
    metricsHistory: state.metricsHistory,
    ratios: state.ratios,
    financialHealth: state.financialHealth,
    trends: state.trends,
    currentPeriod: state.currentPeriod,
    
    // Análisis avanzado
    comparison: getDetailedComparison(),
    projections: projectFutureMetrics(),
    
    // Estados
    loading: state.loading,
    isLoadingAny,
    hasCompleteData,
    error: error || apiError,
    
    // Configuración
    periodType: state.periodType,
    autoUpdate: state.autoUpdate,
    
    // Métodos de carga
    loadCurrentMetrics,
    loadMetricsHistory,
    loadFinancialRatios,
    loadAllMetrics,
    
    // Métodos de análisis
    calculateFinancialHealth,
    calculateTrends,
    
    // Métodos de actualización
    refreshCriticalMetrics,
    changePeriodType,
    
    // Utilidades
    healthColor,
    clearError: () => setError(null),
  };
};

export default useFinancialMetrics;
  // MÉTODOS DE CARGA PRINCIPAL
  // =====================================================

  /**
   * Cargar métricas actuales del período
   */
  const loadCurrentMetrics = useCallback(async (filters: AnalyticsFilters = {}) => {
    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, metrics: true }
    }));

    try {
      const data = await analyticsApi.getMetrics({
        period: periodType,
        ...filters
      });

      const metricsData = {
        total_income: parseFloat(data.metrics.total_income),
        total_expenses: parseFloat(data.metrics.total_expenses),
        net_balance: parseFloat(data.metrics.net_balance),
        transaction_count: data.metrics.transaction_count,
        income_change: data.comparison?.income_change || 0,
        expense_change: data.comparison?.expense_change || 0,
      };

      setState(prev => ({
        ...prev,
        currentMetrics: metricsData,
        currentPeriod: data.metrics,
        comparison: data.comparison || null,
        loading: { ...prev.loading, metrics: false }
      }));

      setError(null);
      return metricsData;
    } catch (err: any) {
      console.error('Error loading current metrics:', err);
      setError(err.message || 'Error al cargar métricas actuales');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, metrics: false }
      }));
      throw err;
    }
  }, [periodType]);

  /**
   * Cargar historial de métricas
   */
  const loadMetricsHistory = useCallback(async (limit: number = 12) => {
    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, history: true }
    }));

    try {
      const data = await analyticsApi.getFinancialMetrics({
        period_type: periodType,
        limit
      });

      setState(prev => ({
        ...prev,
        metricsHistory: data.metrics,
        loading: { ...prev.loading, history: false }
      }));

      setError(null);
      return data.metrics;
    } catch (err: any) {
      console.error('Error loading metrics history:', err);
      setError(err.message || 'Error al cargar historial de métricas');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, history: false }
      }));
      throw err;
    }
  }, [periodType]);

  /**
   * Cargar ratios financieros
   */
  const loadFinancialRatios = useCallback(async (filters: AnalyticsFilters = {}) => {
    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, ratios: true }
    }));

    try {
      const ratiosData = await analyticsApi.getFinancialRatios({
        period: periodType,
        ...filters
      });

      // Extraer solo los ratios del response
      const ratios: FinancialRatios = {
        savings_rate: ratiosData.savings_rate,
        expense_ratio: ratiosData.expense_ratio,
        debt_to_income: ratiosData.debt_to_income,
        liquidity_ratio: ratiosData.liquidity_ratio,
        net_worth_growth: ratiosData.net_worth_growth
      };

      setState(prev => ({
        ...prev,
        ratios,
        loading: { ...prev.loading, ratios: false }
      }));

      setError(null);
      return ratios;
    } catch (err: any) {
      console.error('Error loading financial ratios:', err);
      setError(err.message || 'Error al cargar ratios financieros');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, ratios: false }
      }));
      throw err;
    }
  }, [periodType]);

  /**
   * Calcular salud financiera
   */
  const calculateFinancialHealth = useCallback(async () => {
    if (!state.currentMetrics || !state.ratios) return null;

    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, health: true }
    }));

    try {
      const { currentMetrics, ratios } = state;

      // Factores de salud financiera con pesos
      const factors = {
        savings_rate: {
          value: ratios.savings_rate,
          weight: 0.3,
          score: calculateSavingsScore(ratios.savings_rate)
        },
        expense_ratio: {
          value: ratios.expense_ratio,
          weight: 0.25,
          score: calculateExpenseScore(ratios.expense_ratio)
        },
        income_stability: {
          value: Math.abs(currentMetrics.income_change),
          weight: 0.25,
          score: calculateStabilityScore(Math.abs(currentMetrics.income_change))
        },
        debt_ratio: {
          value: ratios.debt_to_income || 0,
          weight: 0.2,
          score: calculateDebtScore(ratios.debt_to_income || 0)
        }
      };

      // Calcular puntuación total
      const totalScore = Object.values(factors).reduce((sum, factor) => 
        sum + (factor.score * factor.weight), 0
      );

      // Determinar nivel
      let level: FinancialHealth['level'];
      if (totalScore >= 80) level = 'excellent';
      else if (totalScore >= 65) level = 'good';
      else if (totalScore >= 45) level = 'fair';
      else level = 'poor';

      // Generar recomendaciones
      const recommendations = generateRecommendations(factors, ratios);

      const health: FinancialHealth = {
        score: Math.round(totalScore),
        level,
        factors,
        recommendations
      };

      setState(prev => ({
        ...prev,
        financialHealth: health,
        loading: { ...prev.loading, health: false }
      }));

      return health;
    } catch (err: any) {
      console.error('Error calculating financial health:', err);
      setError(err.message || 'Error al calcular salud financiera');
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, health: false }
      }));
      throw err;
    }
  }, [state.currentMetrics, state.ratios]);

  // =====================================================
  // FUNCIONES DE SCORING
  // =====================================================

  const calculateSavingsScore = (savingsRate: number): number => {
    if (savingsRate >= 30) return 100;
    if (savingsRate >= 20) return 85;
    if (savingsRate >= 15) return 70;
    if (savingsRate >= 10) return 55;
    if (savingsRate >= 5) return 35;
    return 15;
  };

  const calculateExpenseScore = (expenseRatio: number): number => {
    if (expenseRatio <= 50) return 100;
    if (expenseRatio <= 70) return 85;
    if (expenseRatio <= 85) return 70;
    if (expenseRatio <= 95) return 45;
    return 20;
  };

  const calculateStabilityScore = (volatility: number): number => {
    if (volatility <= 5) return 100;
    if (volatility <= 15) return 80;
    if (volatility <= 30) return 60;
    if (volatility <= 50) return 40;
    return 20;
  };

  const calculateDebtScore = (debtRatio: number): number => {
    if (debtRatio <= 20) return 100;
    if (debtRatio <= 36) return 75;
    if (debtRatio <= 50) return 50;
    if (debtRatio <= 70) return 25;
    return 10;
  };

  // =====================================================
  // GENERACIÓN DE RECOMENDACIONES
  // =====================================================

  const generateRecommendations = (
    factors: FinancialHealth['factors'], 
    ratios: FinancialRatios
  ): string[] => {
    const recommendations: string[] = [];

    // Recomendaciones por tasa de ahorro
    if (factors.savings_rate.value < 10) {
      recommendations.push('Aumenta tu tasa de ahorro al menos al 10% de tus ingresos');
    } else if (factors.savings_rate.value < 20) {
      recommendations.push('¡Buen progreso! Intenta alcanzar una tasa de ahorro del 20%');
    }

    // Recomendaciones por ratio de gastos
    if (factors.expense_ratio.value > 90) {
      recommendations.push('Tus gastos son muy altos. Revisa y reduce gastos no esenciales');
    } else if (factors.expense_ratio.value > 70) {
      recommendations.push('Controla mejor tus gastos para mejorar tu situación financiera');
    }

    // Recomendaciones por estabilidad de ingresos
    if (factors.income_stability.value > 30) {
      recommendations.push('Busca diversificar tus fuentes de ingresos para mayor estabilidad');
    }

    // Recomendaciones por deudas
    if (factors.debt_ratio.value > 36) {
      recommendations.push('Reduce tu nivel de endeudamiento para mejorar tu salud financiera');
    }

    // Recomendaciones generales
    if (ratios.net_worth_growth < 0) {
      recommendations.push('Considera estrategias para hacer crecer tu patrimonio neto');
    }

    return recommendations.slice(0, 3); // Máximo 3 recomendaciones
  };

  // =====================================================