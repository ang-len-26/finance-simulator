// =====================================================
// ANALYTICS API SERVICES - Servicios completos para reportes y análisis
// 100% basado en los endpoints reales del backend Django
// =====================================================

import apiClient from '@/services/api/client';
import { ANALYTICS_ENDPOINTS, buildAnalyticsFilters, buildReportPeriodParams, buildAlertParams } from '@/services/api/endpoints';
import type {
  // Interfaces principales
  FinancialMetric,
  FinancialMetricComparison,
  CategorySummary,
  BudgetAlert,
  BudgetAlertDetail,
  
  // Respuestas de endpoints
  MetricsResponse,
  ReportMetrics,
  IncomeVsExpensesResponse,
  BalanceTimelineResponse,
  CategoryDistributionResponse,
  TopCategoriesResponse,
  RecentTransactionsResponse,
  FinancialMetricsResponse,
  AlertsResponse,
  CategoryTrendsResponse,
  ReportsOverview,
  FinancialRatiosResponse,
  MarkAlertsReadRequest,
  MarkAlertsReadResponse,
  
  // Filtros y parámetros
  AnalyticsFilters,
  AlertFilters,
  ReportPeriod,
  PeriodType,
  CustomPeriodConfig
} from '../types/analytics.types';

// =====================================================
// 📊 REPORTES Y MÉTRICAS PRINCIPALES
// =====================================================

/**
 * Métricas principales con comparativas - Para las 4 tarjetas superiores del dashboard
 * GET /api/reports/metrics/
 */
export const getMetrics = async (filters: {
  period?: ReportPeriod;
  start_date?: string;
  end_date?: string;
} = {}): Promise<MetricsResponse> => {
  const params = buildReportPeriodParams(
    filters.period || 'monthly',
    filters.start_date && filters.end_date ? {
      start: filters.start_date,
      end: filters.end_date
    } : undefined
  );
  
  return apiClient.get<MetricsResponse>(ANALYTICS_ENDPOINTS.REPORTS_METRICS, { params });
};

/**
 * Gráfico ingresos vs gastos mensuales - Para gráfico de barras/líneas
 * GET /api/reports/income-vs-expenses/
 */
export const getIncomeVsExpenses = async (): Promise<IncomeVsExpensesResponse> => {
  return apiClient.get<IncomeVsExpensesResponse>(ANALYTICS_ENDPOINTS.REPORTS_INCOME_VS_EXPENSES);
};

/**
 * Timeline de balance acumulado - Para gráfico de línea temporal
 * GET /api/reports/balance-timeline/
 */
export const getBalanceTimeline = async (filters: {
  period?: ReportPeriod;
  start_date?: string;
  end_date?: string;
} = {}): Promise<BalanceTimelineResponse> => {
  const params = buildReportPeriodParams(
    filters.period || 'monthly',
    filters.start_date && filters.end_date ? {
      start: filters.start_date,
      end: filters.end_date
    } : undefined
  );
  
  return apiClient.get<BalanceTimelineResponse>(ANALYTICS_ENDPOINTS.REPORTS_BALANCE_TIMELINE, { params });
};

/**
 * Distribución de gastos por categoría - Para gráfico de dona/pie
 * GET /api/reports/category-distribution/
 */
export const getCategoryDistribution = async (filters: {
  period?: ReportPeriod;
  start_date?: string;
  end_date?: string;
} = {}): Promise<CategoryDistributionResponse> => {
  const params = buildReportPeriodParams(
    filters.period || 'monthly',
    filters.start_date && filters.end_date ? {
      start: filters.start_date,
      end: filters.end_date
    } : undefined
  );
  
  return apiClient.get<CategoryDistributionResponse>(ANALYTICS_ENDPOINTS.REPORTS_CATEGORY_DISTRIBUTION, { params });
};

/**
 * Top 5 categorías con detalles y tendencias
 * GET /api/reports/top-categories/
 */
export const getTopCategories = async (filters: {
  period?: ReportPeriod;
  start_date?: string;
  end_date?: string;
} = {}): Promise<TopCategoriesResponse> => {
  const params = buildReportPeriodParams(
    filters.period || 'monthly',
    filters.start_date && filters.end_date ? {
      start: filters.start_date,
      end: filters.end_date
    } : undefined
  );
  
  return apiClient.get<TopCategoriesResponse>(ANALYTICS_ENDPOINTS.REPORTS_TOP_CATEGORIES, { params });
};

/**
 * Transacciones recientes con íconos para reportes
 * GET /api/reports/recent-transactions/
 */
export const getRecentTransactions = async (limit: number = 10): Promise<RecentTransactionsResponse> => {
  return apiClient.get<RecentTransactionsResponse>(ANALYTICS_ENDPOINTS.REPORTS_RECENT_TRANSACTIONS, {
    params: { limit }
  });
};

/**
 * Métricas financieras precalculadas por período
 * GET /api/reports/financial-metrics/
 */
export const getFinancialMetrics = async (filters: {
  period_type?: PeriodType;
  limit?: number;
} = {}): Promise<FinancialMetricsResponse> => {
  const params = buildAnalyticsFilters(filters);
  
  return apiClient.get<FinancialMetricsResponse>(ANALYTICS_ENDPOINTS.REPORTS_FINANCIAL_METRICS, { params });
};

/**
 * Tendencias de categorías en el tiempo
 * GET /api/reports/category-trends/
 */
export const getCategoryTrends = async (filters: {
  period?: ReportPeriod;
} = {}): Promise<CategoryTrendsResponse> => {
  const params = buildAnalyticsFilters(filters);
  
  return apiClient.get<CategoryTrendsResponse>(ANALYTICS_ENDPOINTS.REPORTS_CATEGORY_TRENDS, { params });
};

// =====================================================
// 🚨 SISTEMA DE ALERTAS
// =====================================================

/**
 * Obtener alertas de presupuesto con filtros
 * GET /api/reports/alerts/
 */
export const getAlerts = async (filters: AlertFilters = {}): Promise<AlertsResponse> => {
  const params = buildAlertParams(filters);
  
  return apiClient.get<AlertsResponse>(ANALYTICS_ENDPOINTS.REPORTS_ALERTS, { params });
};

/**
 * Marcar múltiples alertas como leídas (operación bulk)
 * POST /api/reports/mark-alert-read/
 */
export const markAlertsAsRead = async (alertIds: number[]): Promise<MarkAlertsReadResponse> => {
  const payload: MarkAlertsReadRequest = { alert_ids: alertIds };
  
  return apiClient.post<MarkAlertsReadResponse>(ANALYTICS_ENDPOINTS.REPORTS_MARK_ALERT_READ, payload);
};

// =====================================================
// 📈 ENDPOINTS UNIFICADOS Y ESPECIALES
// =====================================================

/**
 * Dashboard completo en una sola llamada - Optimizado para carga inicial
 * GET /api/reports-overview/
 */
export const getReportsOverview = async (filters: {
  period?: ReportPeriod;
  start_date?: string;
  end_date?: string;
} = {}): Promise<ReportsOverview> => {
  const params = buildReportPeriodParams(
    filters.period || 'monthly',
    filters.start_date && filters.end_date ? {
      start: filters.start_date,
      end: filters.end_date
    } : undefined
  );
  
  return apiClient.get<ReportsOverview>(ANALYTICS_ENDPOINTS.REPORTS_OVERVIEW, { params });
};

/**
 * Ratios financieros profesionales con recomendaciones
 * GET /api/financial-ratios/
 */
export const getFinancialRatios = async (filters: {
  period?: ReportPeriod;
  start_date?: string;
  end_date?: string;
} = {}): Promise<FinancialRatiosResponse> => {
  const params = buildReportPeriodParams(
    filters.period || 'monthly',
    filters.start_date && filters.end_date ? {
      start: filters.start_date,
      end: filters.end_date
    } : undefined
  );
  
  return apiClient.get<FinancialRatiosResponse>(ANALYTICS_ENDPOINTS.FINANCIAL_RATIOS, { params });
};

// =====================================================
// 📋 CRUD DE MÉTRICAS FINANCIERAS (Opcional)
// =====================================================

/**
 * Listar métricas financieras (CRUD básico)
 * GET /api/reports/
 */
export const listFinancialMetrics = async (filters: AnalyticsFilters = {}): Promise<FinancialMetric[]> => {
  const params = buildAnalyticsFilters(filters);
  
  return apiClient.get<FinancialMetric[]>(ANALYTICS_ENDPOINTS.REPORTS, { params });
};

/**
 * Obtener métrica financiera específica
 * GET /api/reports/{id}/
 */
export const getFinancialMetric = async (id: number): Promise<FinancialMetricComparison> => {
  return apiClient.get<FinancialMetricComparison>(ANALYTICS_ENDPOINTS.REPORT_DETAIL(id));
};

/**
 * Crear nueva métrica financiera (normalmente automático)
 * POST /api/reports/
 */
export const createFinancialMetric = async (data: Partial<FinancialMetric>): Promise<FinancialMetric> => {
  return apiClient.post<FinancialMetric>(ANALYTICS_ENDPOINTS.REPORTS, data);
};

/**
 * Actualizar métrica financiera
 * PUT /api/reports/{id}/
 */
export const updateFinancialMetric = async (id: number, data: Partial<FinancialMetric>): Promise<FinancialMetric> => {
  return apiClient.put<FinancialMetric>(ANALYTICS_ENDPOINTS.REPORT_DETAIL(id), data);
};

/**
 * Eliminar métrica financiera
 * DELETE /api/reports/{id}/
 */
export const deleteFinancialMetric = async (id: number): Promise<void> => {
  return apiClient.delete<void>(ANALYTICS_ENDPOINTS.REPORT_DETAIL(id));
};

// =====================================================
// 🛠️ UTILIDADES Y HELPERS
// =====================================================

/**
 * Generar filtros de período predefinidos
 */
export const getPredefinedPeriods = () => {
  const now = new Date();
  const thisMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
  const thisYear = new Date(now.getFullYear(), 0, 1);
  const last30Days = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  const last90Days = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
  
  return {
    thisMonth: {
      period: 'monthly' as ReportPeriod,
      label: 'Este mes',
      start_date: thisMonth.toISOString().split('T')[0],
      end_date: now.toISOString().split('T')[0]
    },
    lastMonth: {
      period: 'custom' as ReportPeriod,
      label: 'Mes pasado',
      start_date: lastMonth.toISOString().split('T')[0],
      end_date: new Date(thisMonth.getTime() - 1).toISOString().split('T')[0]
    },
    thisYear: {
      period: 'yearly' as ReportPeriod,
      label: 'Este año',
      start_date: thisYear.toISOString().split('T')[0],
      end_date: now.toISOString().split('T')[0]
    },
    last30Days: {
      period: 'last_30_days' as ReportPeriod,
      label: 'Últimos 30 días',
      start_date: last30Days.toISOString().split('T')[0],
      end_date: now.toISOString().split('T')[0]
    },
    last90Days: {
      period: 'last_90_days' as ReportPeriod,
      label: 'Últimos 90 días',
      start_date: last90Days.toISOString().split('T')[0],
      end_date: now.toISOString().split('T')[0]
    }
  };
};

/**
 * Validar configuración de período personalizado
 */
export const validateCustomPeriod = (config: CustomPeriodConfig): boolean => {
  const start = new Date(config.start_date);
  const end = new Date(config.end_date);
  const now = new Date();
  
  // Validar que las fechas sean válidas
  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    return false;
  }
  
  // Validar que start sea anterior a end
  if (start >= end) {
    return false;
  }
  
  // Validar que no sea futuro
  if (end > now) {
    return false;
  }
  
  // Validar rango máximo (2 años)
  const maxRange = 2 * 365 * 24 * 60 * 60 * 1000;
  if (end.getTime() - start.getTime() > maxRange) {
    return false;
  }
  
  return true;
};

/**
 * Formatear período para display
 */
export const formatPeriodLabel = (period: ReportPeriod, customPeriod?: CustomPeriodConfig): string => {
  switch (period) {
    case 'monthly':
      return 'Este mes';
    case 'quarterly':
      return 'Este trimestre';
    case 'yearly':
      return 'Este año';
    case 'last_30_days':
      return 'Últimos 30 días';
    case 'last_90_days':
      return 'Últimos 90 días';
    case 'custom':
      if (customPeriod) {
        const start = new Date(customPeriod.start_date).toLocaleDateString();
        const end = new Date(customPeriod.end_date).toLocaleDateString();
        return `${start} - ${end}`;
      }
      return 'Período personalizado';
    default:
      return 'Período';
  }
};

/**
 * Obtener configuración de colores para gráficos
 */
export const getChartColors = () => ({
  // Colores principales
  primary: '#3b82f6',
  secondary: '#6366f1',
  success: '#22c55e',
  warning: '#f59e0b',
  danger: '#ef4444',
  
  // Paleta para categorías
  categories: [
    '#3b82f6', // Azul
    '#ef4444', // Rojo
    '#22c55e', // Verde
    '#f59e0b', // Amarillo
    '#8b5cf6', // Púrpura
    '#ec4899', // Rosa
    '#06b6d4', // Cian
    '#84cc16', // Lima
    '#f97316', // Naranja
    '#6b7280'  // Gris
  ],
  
  // Gradientes
  gradients: {
    income: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
    expense: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    balance: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'
  },
  
  // Transparencias
  alpha: {
    light: '0.1',
    medium: '0.5',
    strong: '0.8'
  }
});

/**
 * Calcular métricas derivadas
 */
export const calculateDerivedMetrics = (metrics: ReportMetrics) => {
  const { total_income, total_expenses } = metrics;
  
  return {
    savings_rate: total_income > 0 ? ((total_income - total_expenses) / total_income) * 100 : 0,
    expense_ratio: total_income > 0 ? (total_expenses / total_income) * 100 : 0,
    net_savings: total_income - total_expenses,
    spending_velocity: total_expenses / 30, // Gasto promedio diario
  };
};

// =====================================================
// OBJETO PRINCIPAL EXPORTADO
// =====================================================

const analyticsApi = {
  // Reportes principales
  getMetrics,
  getIncomeVsExpenses,
  getBalanceTimeline,
  getCategoryDistribution,
  getTopCategories,
  getRecentTransactions,
  getFinancialMetrics,
  getCategoryTrends,
  
  // Sistema de alertas
  getAlerts,
  markAlertsAsRead,
  
  // Endpoints unificados
  getReportsOverview,
  getFinancialRatios,
  
  // CRUD básico (opcional)
  listFinancialMetrics,
  getFinancialMetric,
  createFinancialMetric,
  updateFinancialMetric,
  deleteFinancialMetric,
  
  // Utilidades
  getPredefinedPeriods,
  validateCustomPeriod,
  formatPeriodLabel,
  getChartColors,
  calculateDerivedMetrics,
};

export default analyticsApi;