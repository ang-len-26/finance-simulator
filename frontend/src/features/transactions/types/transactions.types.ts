import { DateRangeFilter, PaginationParams } from "@/types/api.types";

// Basado en transactions/serializers.py
export type TransactionType = 'income' | 'expense' | 'transfer' | 'investment' | 'loan' | 'debt' | 'savings';
export type CategoryType = 'income' | 'expense' | 'both';
export type RecurringFrequency = 'daily' | 'weekly' | 'monthly' | 'yearly';

export interface Category {
  id: number;
  name: string;
  slug: string;
  icon: string;
  color: string;
  category_type: CategoryType;
  parent: number | null;
  parent_name: string | null;
  is_active: boolean;
  sort_order: number;
  transaction_count: number;
  subcategories: Category[];
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: number;
  title: string;
  amount: string;
  type: TransactionType;
  date: string;
  description: string;
  from_account: number | null;
  to_account: number | null;
  from_account_name: string | null;
  to_account_name: string | null;
  category: number | null;
  category_name: string | null;
  category_icon: string | null;
  category_color: string | null;
  reference_number: string;
  location: string;
  tags: string[];
  is_recurring: boolean;
  recurring_frequency: RecurringFrequency | null;
  created_at: string;
  updated_at: string;
}

export interface CreateTransactionData {
  title: string;
  amount: string;
  type: TransactionType;
  date: string;
  description?: string;
  from_account?: number;
  to_account?: number;
  category?: number;
  location?: string;
  tags?: string[];
  is_recurring?: boolean;
  recurring_frequency?: RecurringFrequency;
}

export interface TransactionFilters extends PaginationParams, DateRangeFilter {
  type?: TransactionType;
  category?: number;
  from_account?: number;
  to_account?: number;
  min_amount?: number;
  max_amount?: number;
  search?: string;
  tags?: string[];
}

export interface TransactionDashboard {
  total_income: string;
  total_expenses: string;
  net_balance: string;
  transaction_count: number;
  income_transactions: number;
  expense_transactions: number;
  top_category: string | null;
  recent_transactions: Transaction[];
}

export interface CategoryDistribution {
  category_name: string;
  category_color: string;
  total_amount: number;
  percentage: number;
}