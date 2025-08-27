import { Transaction } from "@/features/transactions/types/transactions.types";
import { DateRangeFilter } from "@/types/api.types";

// Basado en analytics/serializers.py
export type PeriodType = 'monthly' | 'quarterly' | 'yearly' | 'custom';
export type AlertType = 'budget_exceeded' | 'goal_behind' | 'unusual_expense' | 'low_balance';

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

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
    fill?: boolean;
  }[];
}

export interface MetricsComparison {
  current_period: FinancialMetric;
  previous_period: FinancialMetric | null;
  income_change: number;
  expense_change: number;
  balance_change: number;
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

export interface ReportsOverview {
  metrics: FinancialMetric;
  income_vs_expenses: ChartData;
  category_distribution: ChartData;
  balance_timeline: ChartData;
  top_categories: CategorySummary[];
  recent_transactions: Transaction[];
  alerts: BudgetAlert[];
}