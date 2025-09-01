import { DateRangeFilter } from "@/types/api.types";

// =====================================================
// TIPOS BÁSICOS Y ENUMS
// =====================================================
export type PeriodType = 'monthly' | 'quarterly' | 'yearly' | 'custom';
export type AlertType = 'budget_exceeded' | 'goal_behind' | 'unusual_expense' | 'low_balance';
export type ReportPeriod = 'monthly' | 'quarterly' | 'yearly' | 'last_30_days' | 'last_90_days' | 'custom';

// =====================================================
// INTERFACES PRINCIPALES
// =====================================================

export interface FinancialMetric {
  id: number;
  period_type: PeriodType;
  period_start: string;
  period_end: string;
  period_label: string;
  total_income: string;
  total_expenses: string;
  net_balance: string;
  checking_balance: string;
  savings_balance: string;
  investment_balance: string;
  credit_balance: string;
  transaction_count: number;
  top_expense_category: string | null;
  top_expense_amount: string;
  calculated_at: string;
}

export interface CategorySummary {
  id: number;
  category_name: string;
  category_color: string;
  category_icon: string;
  period_start: string;
  period_end: string;
  total_amount: string;
  transaction_count: number;
  percentage_of_total: number;
  previous_period_amount: string | null;
  change_percentage: number | null;
  average_per_transaction: string;
}

export interface BudgetAlert {
  id: number;
  alert_type: AlertType;
  title: string;
  message: string;
  severity: 'low' | 'medium' | 'high';
  is_read: boolean;
  created_at: string;
  related_category: number | null;
  related_goal: number | null;
  related_account: number | null;
}

export interface BudgetAlertDetail extends BudgetAlert {
  description?: string;
  action_url?: string;
  metadata?: Record<string, any>;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
    fill?: boolean;
    tension?: number;
    pointRadius?: number;
    pointHoverRadius?: number;
  }[];
}

export interface MetricsComparison {
  current_period: FinancialMetric;
  previous_period: FinancialMetric | null;
  income_change: number;
  expense_change: number;
  balance_change: number;
}

export interface FinancialMetricComparison {
  metric: FinancialMetric;
  comparison: MetricsComparison | null;
  trends: {
    income_trend: 'up' | 'down' | 'stable';
    expense_trend: 'up' | 'down' | 'stable';
    balance_trend: 'up' | 'down' | 'stable';
  };
}

export interface AnalyticsFilters extends DateRangeFilter {
  period?: PeriodType;
  category?: number;
  account?: number;
}

export interface FinancialRatios {
  savings_rate: number;
  expense_ratio: number;
  debt_to_income: number;
  liquidity_ratio: number;
  net_worth_growth: number;
}

export interface FinancialRatiosData extends FinancialRatios {
  investment_rate?: number;
  emergency_fund_ratio?: number;
  debt_service_ratio?: number;
}

// =====================================================
// TIPOS PARA PERÍODOS Y CONFIGURACIÓN
// =====================================================

export interface AnalyticsPeriod {
  type: PeriodType;
  start_date: string;
  end_date: string;
  label: string;
}

export interface CustomPeriodConfig {
  start_date: string;
  end_date: string;
}

// =====================================================
// TIPOS PARA INSIGHTS Y TENDENCIAS
// =====================================================

export interface TopCategory {
  category_name: string;
  category_color: string;
  category_icon: string;
  total_amount: number;
  percentage_of_total: number;
  transaction_count: number;
  change_percentage?: number;
  trend?: 'up' | 'down' | 'stable';
}

export interface RecentTransaction {
  id: number;
  amount: string;
  description: string;
  category_name: string;
  category_icon: string;
  category_color: string;
  account_name: string;
  transaction_date: string;
  transaction_type: 'income' | 'expense';
}

export interface CategoryTrendData {
  category_id: number;
  category_name: string;
  category_color: string;
  category_icon: string;
  periods: Array<{
    period_start: string;
    period_end: string;
    period_label: string;
    total_amount: number;
    transaction_count: number;
    change_percentage: number | null;
  }>;
  overall_trend: 'up' | 'down' | 'stable';
  total_change_percentage: number;
}

// =====================================================
// TIPOS PARA RESPUESTAS DE API
// =====================================================

export interface ReportMetrics {
  total_income: number;
  total_expenses: number;
  net_balance: number;
  transaction_count: number;
  checking_balance: number;
  savings_balance: number;
  investment_balance: number;
  credit_balance: number;
}

export interface MetricsResponse {
  metrics: FinancialMetric;
  comparison: MetricsComparison | null;
  period: string;
  summary: {
    income_change: number;
    expense_change: number;
    balance_change: number;
    savings_rate: number;
    expense_ratio: number;
  };
}

export interface IncomeVsExpensesResponse {
  chart_data: ChartData;
  summary: {
    total_income: number;
    total_expenses: number;
    net_balance: number;
    period_count: number;
  };
  net_balance_data?: ChartData;
  metadata?: {
    period_type: string;
    currency: string;
  };
}

export interface BalanceTimelineResponse {
  chart_data: ChartData;
  summary: {
    starting_balance: number;
    ending_balance: number;
    total_change: number;
    change_percentage: number;
    peak_balance: number;
    lowest_balance: number;
  };
  metadata?: {
    period_type: string;
    data_points: number;
  };
}

export interface CategoryDistributionResponse {
  chart_data: ChartData;
  summary: {
    total_amount: number;
    category_count: number;
    top_category: {
      name: string;
      amount: number;
      percentage: number;
    };
    smallest_category: {
      name: string;
      amount: number;
      percentage: number;
    };
  };
  categories: CategorySummary[];
}

export interface TopCategoriesResponse {
  categories: CategorySummary[];
  summary: {
    total_categories: number;
    total_amount: number;
    top_5_percentage: number;
  };
  period: AnalyticsPeriod;
}

export interface RecentTransactionsResponse {
  transactions: RecentTransaction[];
  summary: {
    total_count: number;
    income_count: number;
    expense_count: number;
    total_income: number;
    total_expenses: number;
  };
  metadata: {
    limit: number;
    has_more: boolean;
  };
}

export interface FinancialMetricsResponse {
  metrics: FinancialMetric[];
  summary: {
    periods_count: number;
    date_range: {
      start: string;
      end: string;
    };
    totals: {
      income: number;
      expenses: number;
      net_balance: number;
    };
  };
  metadata: {
    period_type: PeriodType;
    currency: string;
  };
}

export interface CategoryTrendsResponse {
  trends: CategoryTrendData[];
  summary: {
    categories_count: number;
    periods_analyzed: number;
    trending_up: number;
    trending_down: number;
    stable: number;
  };
  period: AnalyticsPeriod;
}

export interface AlertsResponse {
  alerts: BudgetAlert[];
  summary: {
    total_count: number;
    unread_count: number;
    by_severity: {
      high: number;
      medium: number;
      low: number;
    };
    by_type: Record<AlertType, number>;
  };
  metadata: {
    last_check: string;
    auto_generated: boolean;
  };
}

export interface FinancialRatiosResponse extends FinancialRatiosData {
  period: AnalyticsPeriod;
  benchmarks: {
    savings_rate: { poor: number; fair: number; good: number; excellent: number };
    expense_ratio: { poor: number; fair: number; good: number; excellent: number };
    debt_to_income: { poor: number; fair: number; good: number; excellent: number };
  };
  recommendations: string[];
  score: {
    overall: number;
    level: 'poor' | 'fair' | 'good' | 'excellent';
  };
}

export interface ReportsOverview {
  metrics: FinancialMetric;
  income_vs_expenses: ChartData;
  category_distribution: ChartData;
  balance_timeline: ChartData;
  top_categories: CategorySummary[];
  recent_transactions: RecentTransaction[];
  alerts: BudgetAlert[];
  financial_health: {
    score: number;
    level: 'poor' | 'fair' | 'good' | 'excellent';
    factors: string[];
  };
  summary: {
    period_label: string;
    data_freshness: string;
    currency: string;
  };
}

// =====================================================
// TIPOS PARA REQUESTS
// =====================================================

export interface AlertFilters {
  severity?: 'low' | 'medium' | 'high';
  alert_type?: AlertType;
  is_read?: boolean;
  created_after?: string;
  created_before?: string;
  category?: number;
  account?: number;
}

export interface MarkAlertsReadRequest {
  alert_ids: number[];
}

export interface MarkAlertsReadResponse {
  updated_count: number;
  alerts: BudgetAlert[];
  success: boolean;
  message: string;
}