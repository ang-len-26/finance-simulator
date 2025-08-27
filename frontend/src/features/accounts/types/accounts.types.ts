import { PaginationParams } from "@/types/api.types";

// Basado en accounts/serializers.py
export type AccountType = 'checking' | 'savings' | 'credit' | 'investment' | 'cash';
export type Currency = 'PEN' | 'USD' | 'EUR';

export interface Account {
  id: number;
  name: string;
  bank_name: string;
  account_number: string;
  account_type: AccountType;
  initial_balance: string;
  current_balance: string;
  currency: Currency;
  is_active: boolean;
  include_in_reports: boolean;
  transaction_count: number;
  last_transaction_date: string | null;
  monthly_income: number;
  monthly_expenses: number;
  created_at: string;
  updated_at: string;
}

export interface AccountSummary {
  total_balance: string;
  checking_balance: string;
  savings_balance: string;
  credit_balance: string;
  investment_balance: string;
  cash_balance: string;
  total_accounts: number;
  active_accounts: number;
  monthly_income: string;
  monthly_expenses: string;
  net_worth: string;
}

export interface CreateAccountData {
  name: string;
  bank_name: string;
  account_number: string;
  account_type: AccountType;
  initial_balance: string;
  currency: Currency;
  is_active?: boolean;
  include_in_reports?: boolean;
}

export interface AccountFilters extends PaginationParams {
  is_active?: boolean;
  account_type?: AccountType;
  currency?: Currency;
  min_balance?: number;
  max_balance?: number;
  search?: string;
}

export interface BalanceHistoryPoint {
  date: string;
  balance: number;
}

export interface ReconcileAccountData {
  actual_balance: string;
  notes?: string;
}