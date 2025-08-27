import { PaginationParams } from "@/types/api.types";

// Basado en goals/serializers.py
export type GoalType = 'savings' | 'debt_payment' | 'investment' | 'purchase' | 'emergency_fund' | 'retirement' | 'education' | 'vacation';
export type GoalStatus = 'active' | 'completed' | 'paused' | 'cancelled';
export type Priority = 'low' | 'medium' | 'high';
export type ReminderFrequency = 'daily' | 'weekly' | 'monthly';

export interface GoalMilestone {
  id: number;
  goal: number;
  title: string;
  target_amount: string;
  target_date: string;
  is_achieved: boolean;
  achieved_date: string | null;
  sort_order: number;
}

export interface GoalContribution {
  id: number;
  goal: number;
  amount: string;
  date: string;
  description: string;
  transaction: number | null;
  created_at: string;
}

export interface FinancialGoal {
  id: number;
  title: string;
  description: string;
  goal_type: GoalType;
  goal_type_label: string;
  target_amount: string;
  current_amount: string;
  progress_percentage: number;
  remaining_amount: string;
  start_date: string;
  target_date: string;
  days_remaining: number;
  is_overdue: boolean;
  monthly_target: string | null;
  auto_contribution: boolean;
  suggested_monthly_amount: string;
  associated_account: number | null;
  associated_account_name: string | null;
  related_categories: number[];
  status: GoalStatus;
  status_label: string;
  priority: Priority;
  priority_label: string;
  is_public: boolean;
  icon: string;
  color: string;
  enable_reminders: boolean;
  reminder_frequency: ReminderFrequency | null;
  milestones: GoalMilestone[];
  contributions: GoalContribution[];
  contributions_count: number;
  last_contribution_date: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface GoalTemplate {
  id: number;
  title: string;
  description: string;
  goal_type: GoalType;
  suggested_amount: string | null;
  suggested_duration_months: number | null;
  category: string;
  icon: string;
  color: string;
  is_active: boolean;
  sort_order: number;
}

export interface CreateGoalData {
  title: string;
  description?: string;
  goal_type: GoalType;
  target_amount: string;
  target_date: string;
  associated_account?: number;
  related_categories?: number[];
  priority?: Priority;
  enable_reminders?: boolean;
  reminder_frequency?: ReminderFrequency;
  auto_contribution?: boolean;
  template?: number;
}

export interface GoalFilters extends PaginationParams {
  status?: GoalStatus;
  goal_type?: GoalType;
  priority?: Priority;
  min_progress?: number;
  max_progress?: number;
  is_overdue?: boolean;
  search?: string;
}

export interface GoalSummary {
  total_goals: number;
  active_goals: number;
  completed_goals: number;
  total_saved: string;
  total_target: string;
  average_progress: number;
  upcoming_targets: FinancialGoal[];
}

export interface CreateContributionData {
  amount: string;
  date: string;
  description?: string;
}