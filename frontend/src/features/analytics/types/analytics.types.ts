// =====================================================
// ANALYTICS TYPES - 100% alineado con backend Django
// Basado en models.py, serializers.py y views.py reales
// =====================================================

import { DateRangeFilter } from "@/types/api.types";

// =====================================================
// ENUMS Y CONSTANTES DEL BACKEND
// =====================================================

// Tipos de período (FinancialMetric.PERIOD_TYPES)
export type PeriodType = 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';

// Períodos extendidos para reportes (views.py)
export type ReportPeriod = PeriodType | 'last_30_days' | 'last_90_days' | 'custom';

// Tipos de alerta (BudgetAlert.ALERT_TYPES)
export type AlertType = 
  | 'budget_exceeded' 
  | 'unusual_expense' 
  | 'income_drop' 
  | 'account_low' 
  | 'category_spike';

// Niveles de severidad (BudgetAlert.SEVERITY_LEVELS)
export type SeverityLevel = 'low' | 'medium' | 'high' | 'critical';

// =====================================================
// INTERFACES PRINCIPALES DEL BACKEND
// =====================================================

/**
 * FinancialMetric - Basado en models.py y FinancialMetricSerializer
 */
export interface FinancialMetric {
  id: number;
  period_type: PeriodType;
  period_start: string; // YYYY-MM-DD
  period_end: string;   // YYYY-MM-DD
  period_label: string; // Calculado: "Enero 2024", "Q1 2024", etc.
  
  // Métricas principales
  total_income: string;      // Decimal como string
  total_expenses: string;    // Decimal como string
  net_balance: string;       // Decimal como string
  
  // Métricas por tipo de cuenta
  checking_balance: string;
  savings_balance: string;
  investment_balance: string;
  credit_balance: string;
  
  // Estadísticas
  transaction_count: number;
  top_expense_category: number | null; // FK a Category
  top_expense_amount: string;          // Decimal como string
  
  // Metadatos
  calculated_at: string; // ISO timestamp
  created_at?: string;   // ISO timestamp
}

/**
 * FinancialMetric con comparativas - FinancialMetricComparisonSerializer
 */
export interface FinancialMetricComparison extends FinancialMetric {
  savings_rate: number;  // Calculado como property
  expense_ratio: number; // Calculado como property
  previous_period_comparison: {
    income_change: number;    // Porcentaje
    expense_change: number;   // Porcentaje
    balance_change: number;   // Porcentaje
    previous_period: {
      total_income: number;
      total_expenses: number;
      net_balance: number;
    };
  } | null;
}

/**
 * CategorySummary - Basado en models.py y CategorySummaryReportSerializer
 */
export interface CategorySummary {
  id: number;
  category_name: string;
  category_icon: string;
  category_color: string;
  period_start: string;
  period_end: string;
  period_type: PeriodType;
  
  // Totales
  total_amount: string;         // Decimal como string
  transaction_count: number;
  average_amount: string;       // Decimal como string
  
  // Comparativas
  previous_period_amount: string; // Decimal como string
  percentage_change: string;      // Decimal como string
  most_used_account_name: string | null;
}

/**
 * BudgetAlert - Basado en models.py y BudgetAlertSerializer
 */
export interface BudgetAlert {
  id: number;
  alert_type: AlertType;
  alert_type_label: string; // Display name
  severity: SeverityLevel;
  severity_label: string;   // Display name
  
  // Contenido
  title: string;
  message: string;
  
  // Montos relacionados
  threshold_amount: string | null; // Decimal como string
  actual_amount: string | null;    // Decimal como string
  
  // Relaciones (nombres para UI)
  related_transaction_title: string | null;
  related_category_name: string | null;
  related_account_name: string | null;
  
  // Estado
  is_read: boolean;
  is_dismissed: boolean;
  created_at: string; // ISO timestamp
}

/**
 * BudgetAlert detallado - BudgetAlertDetailSerializer
 */
export interface BudgetAlertDetail extends BudgetAlert {
  related_transaction_details: {
    id: number;
    title: string;
    amount: string;
    date: string;
  } | null;
  
  related_category_details: {
    name: string;
    icon: string;
    color: string;
  } | null;
  
  related_account_details: {
    name: string;
    account_type: string;
    current_balance: string;
  } | null;
  
  days_since_created: number; // Calculado como property
  is_active: boolean;         // Calculado como property
}

// =====================================================
// INTERFACES PARA REPORTES Y GRÁFICOS
// =====================================================

/**
 * Datos para gráficos Chart.js - ChartDataSerializer
 */
export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string | string[];
  borderWidth?: number;
  fill?: boolean;
  tension?: number; // Para gráficos de línea
}

/**
 * Métricas principales para dashboard - views.py metrics()
 */
export interface ReportMetrics {
  total_income: number;
  total_expenses: number;
  net_balance: number;
  transaction_count: number;
  income_change: number;    // Porcentaje vs período anterior
  expense_change: number;   // Porcentaje vs período anterior
}

/**
 * Top categorías con comparativas - views.py top_categories()
 */
export interface TopCategory {
  name: string;
  icon: string;
  color: string;
  current_amount: number;
  previous_amount: number;
  change_percentage: number;
  transaction_count: number;
  average_amount: number;
}

/**
 * Transacción reciente para reportes - views.py recent_transactions()
 */
export interface RecentTransaction {
  id: number;
  title: string;
  amount: number;
  type: string;
  date: string;           // Formato: "15 de Enero"
  icon: string;
  from_account: string | null;
  to_account: string | null;
  category: string | null;
  is_positive: boolean;
}

/**
 * Ratios financieros - financial_ratios()
 */
export interface FinancialRatios {
  savings_rate: number;       // Porcentaje
  expense_ratio: number;      // Porcentaje
  investment_rate: number;    // Porcentaje
  net_worth_change: number;   // Monto absoluto
}

/**
 * Recomendaciones financieras - financial_ratios()
 */
export interface FinancialRecommendations {
  savings: 'Excelente' | 'Bueno' | 'Mejorar';
  expenses: 'Controlado' | 'Revisar' | 'Crítico';
}

// =====================================================
// INTERFACES PARA RESPUESTAS DE ENDPOINTS
// =====================================================

/**
 * Respuesta de /reports/metrics/ - views.py metrics()
 */
export interface MetricsResponse {
  period: {
    start_date: string;
    end_date: string;
    type: ReportPeriod;
  };
  metrics: ReportMetrics;
  previous_period: {
    total_income: number;
    total_expenses: number;
    start_date: string;
    end_date: string;
  };
}

/**
 * Respuesta de /reports/income-vs-expenses/ - views.py income_vs_expenses()
 */
export interface IncomeVsExpensesResponse {
  chart_data: ChartData;
  net_balance_data: number[];
  summary: {
    total_months: number;
    avg_income: number;
    avg_expenses: number;
  };
}

/**
 * Respuesta de /reports/balance-timeline/ - views.py balance_timeline()
 */
export interface BalanceTimelineResponse {
  chart_data: ChartData;
  summary: {
    current_balance: number;
    initial_balance: number;
    trend: number;
    trend_percentage: number;
    highest_balance: number;
    lowest_balance: number;
  };
}

/**
 * Respuesta de /reports/category-distribution/ - views.py category_distribution()
 */
export interface CategoryDistributionResponse {
  chart_data: ChartData;
  summary: {
    total_amount: number;
    category_count: number;
    average_per_category: number;
    top_category: {
      name: string | null;
      amount: number;
      percentage: number;
    };
  };
}

/**
 * Respuesta de /reports/top-categories/ - views.py top_categories()
 */
export interface TopCategoriesResponse {
  categories: TopCategory[];
  period: {
    current: {
      start: string;
      end: string;
    };
    previous: {
      start: string;
      end: string;
    };
  };
}

/**
 * Respuesta de /reports/recent-transactions/ - views.py recent_transactions()
 */
export interface RecentTransactionsResponse {
  transactions: RecentTransaction[];
  total_count: number;
}

/**
 * Respuesta de /reports/financial-metrics/ - views.py financial_metrics()
 */
export interface FinancialMetricsResponse {
  metrics: FinancialMetric[];
  period_type: PeriodType;
  total_periods: number;
  message?: string;      // Si no hay datos
  suggestion?: string;   // Recomendación alternativa
}

/**
 * Respuesta de /reports/alerts/ - views.py alerts()
 */
export interface AlertsResponse {
  alerts: BudgetAlert[];
  summary: {
    total_alerts: number;
    unread_count: number;
    critical_count: number;
  };
}

/**
 * Respuesta de /reports/category-trends/ - views.py category_trends()
 */
export interface CategoryTrendsResponse {
  trends: Array<{
    period: string;
    start_date: string;
    end_date: string;
    categories: Array<{
      category__name: string;
      category__color: string;
      total: number;
    }>;
  }>;
  period_type: ReportPeriod;
}

/**
 * Respuesta completa de /reports-overview/ - reports_overview()
 */
export interface ReportsOverview {
  metrics: ReportMetrics;
  period: {
    start_date: string;
    end_date: string;
    type: ReportPeriod;
  };
  charts: {
    income_vs_expenses: ChartData;
    balance_timeline: ChartData;
    category_distribution: ChartData;
  };
  insights: {
    top_categories: TopCategory[];
    recent_transactions: RecentTransaction[];
    balance_summary: {
      current_balance: number;
      initial_balance: number;
      trend: number;
      trend_percentage: number;
      highest_balance: number;
      lowest_balance: number;
    };
  };
}

/**
 * Respuesta de /financial-ratios/ - financial_ratios()
 */
export interface FinancialRatiosResponse {
  ratios: FinancialRatios;
  recommendations: FinancialRecommendations;
}

// =====================================================
// INTERFACES PARA FILTROS Y PARÁMETROS
// =====================================================

/**
 * Filtros para endpoints de analytics
 */
export interface AnalyticsFilters extends DateRangeFilter {
  period?: ReportPeriod;
  period_type?: PeriodType;
  category?: number;
  account?: number;
  limit?: number;
}

/**
 * Filtros específicos para alertas
 */
export interface AlertFilters {
  severity?: SeverityLevel;
  alert_type?: AlertType;
  is_read?: boolean;
  include_dismissed?: boolean;
  limit?: number;
}

/**
 * Parámetros para marcar alertas como leídas
 */
export interface MarkAlertsReadRequest {
  alert_ids: number[];
}

/**
 * Respuesta de marcar alertas como leídas
 */
export interface MarkAlertsReadResponse {
  message: string;
  updated_count: number;
}

// =====================================================
// TIPOS AUXILIARES
// =====================================================

/**
 * Tendencia de datos (para UI)
 */
export type TrendDirection = 'up' | 'down' | 'stable';

/**
 * Estado de carga para métricas
 */
export interface MetricsLoadingState {
  metrics: boolean;
  charts: boolean;
  alerts: boolean;
  overview: boolean;
}

/**
 * Configuración de período personalizado
 */
export interface CustomPeriodConfig {
  start_date: string;  // YYYY-MM-DD
  end_date: string;    // YYYY-MM-DD
}

/**
 * Configuración de dashboard
 */
export interface DashboardConfig {
  period: ReportPeriod;
  customPeriod?: CustomPeriodConfig;
  showAlerts: boolean;
  showRecentTransactions: boolean;
  chartsToShow: ('income_vs_expenses' | 'balance_timeline' | 'category_distribution')[];
}

/**
 * Resumen de alertas para UI
 */
export interface AlertsSummary {
  total: number;
  unread: number;
  critical: number;
  byType: Record<AlertType, number>;
  bySeverity: Record<SeverityLevel, number>;
}

/**
 * Configuración de alerta
 */
export interface AlertConfig {
  enableNotifications: boolean;
  severityFilter: SeverityLevel[];
  typeFilter: AlertType[];
  autoMarkRead: boolean;
}

/**
 * Insight financiero generado
 */
export interface FinancialInsight {
  type: 'positive' | 'warning' | 'negative' | 'neutral';
  title: string;
  description: string;
  value?: number;
  trend?: TrendDirection;
  category?: string;
  action?: string; // Acción recomendada
}