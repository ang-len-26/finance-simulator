// =====================================================
// GOALS TYPES - Tipos de datos para Metas Financieras
// Rama 5 - 100% alineado con backend/api/goals/
// =====================================================

import { BaseFilterParams } from '@/types/api.types';

// =====================================================
// ENUMS Y CONSTANTES (desde models.py)
// =====================================================

export const GOAL_TYPES = {
  savings: 'Ahorro',
  expense_reduction: 'Reducir Gastos',
  income_increase: 'Aumentar Ingresos',
  debt_payment: 'Pagar Deuda',
  emergency_fund: 'Fondo de Emergencia',
  investment: 'Inversión',
  purchase: 'Compra Específica',
  vacation: 'Vacaciones',
  education: 'Educación',
  retirement: 'Jubilación',
  other: 'Otro',
} as const;

export const GOAL_STATUS = {
  active: 'Activa',
  paused: 'Pausada',
  completed: 'Completada',
  cancelled: 'Cancelada',
  overdue: 'Vencida',
} as const;

export const PRIORITY_LEVELS = {
  low: 'Baja',
  medium: 'Media',
  high: 'Alta',
  critical: 'Crítica',
} as const;

export const CONTRIBUTION_TYPES = {
  manual: 'Aporte Manual',
  automatic: 'Aporte Automático',
  transaction_based: 'Basado en Transacción',
  transfer: 'Transferencia',
} as const;

export const REMINDER_FREQUENCY = {
  daily: 'Diario',
  weekly: 'Semanal',
  monthly: 'Mensual',
} as const;

// Tipos derivados de las constantes
export type GoalType = keyof typeof GOAL_TYPES;
export type GoalStatus = keyof typeof GOAL_STATUS;
export type PriorityLevel = keyof typeof PRIORITY_LEVELS;
export type ContributionType = keyof typeof CONTRIBUTION_TYPES;
export type ReminderFrequency = keyof typeof REMINDER_FREQUENCY;

// =====================================================
// INTERFACES PRINCIPALES - GOALS
// =====================================================

// Hito de meta (GoalMilestone model)
export interface GoalMilestone {
  id: number;
  title: string;
  description?: string;
  target_amount: string; // Decimal como string
  target_date: string; // ISO date
  is_completed: boolean;
  completed_at?: string; // ISO datetime
  icon: string; // Lucide icon name
  order: number;
  progress_percentage: number; // ReadOnly - calculado
}

// Contribución a meta (GoalContribution model)
export interface GoalContribution {
  id: number;
  amount: string; // Decimal como string
  contribution_type: ContributionType;
  date: string; // ISO date
  from_account: number; // FK a Account
  from_account_name: string; // ReadOnly
  related_transaction?: number; // FK opcional a Transaction
  related_transaction_title?: string; // ReadOnly
  notes?: string;
  is_recurring: boolean;
  created_at: string; // ISO datetime
}

// Meta financiera principal (FinancialGoal model)
export interface FinancialGoal {
  id: number;
  title: string;
  description?: string;
  goal_type: GoalType;
  goal_type_label: string; // ReadOnly - get_goal_type_display()
  
  // Montos
  target_amount: string; // Decimal como string
  current_amount: string; // ReadOnly - calculado
  progress_percentage: number; // ReadOnly - calculado
  remaining_amount: string; // ReadOnly - calculado
  
  // Fechas
  start_date: string; // ISO date
  target_date: string; // ISO date
  days_remaining: number; // ReadOnly - calculado
  is_overdue: boolean; // ReadOnly - calculado
  
  // Contribuciones
  monthly_target?: string; // Decimal como string
  auto_contribution?: string; // Decimal como string
  suggested_monthly_amount: string; // ReadOnly - calculado
  
  // Relaciones
  associated_account?: number; // FK opcional a Account
  associated_account_name?: string; // ReadOnly
  related_categories: number[]; // ManyToMany a Category
  
  // Estado y configuración
  status: GoalStatus;
  status_label: string; // ReadOnly - get_status_display()
  priority: PriorityLevel;
  priority_label: string; // ReadOnly - get_priority_display()
  is_public: boolean;
  
  // Configuración visual
  icon: string; // Lucide icon name
  color: string; // Hex color
  
  // Recordatorios
  enable_reminders: boolean;
  reminder_frequency: ReminderFrequency;
  
  // Relaciones anidadas (ReadOnly)
  milestones: GoalMilestone[];
  contributions: GoalContribution[];
  contributions_count: number; // ReadOnly
  last_contribution_date?: string; // ReadOnly
  
  // Metadatos
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
  completed_at?: string; // ISO datetime
}

// Versión ligera para listados (FinancialGoalSummarySerializer)
export interface FinancialGoalSummary {
  id: number;
  title: string;
  goal_type: GoalType;
  goal_type_label: string;
  target_amount: string;
  current_amount: string;
  progress_percentage: number;
  remaining_amount: string;
  target_date: string;
  days_remaining: number;
  status: GoalStatus;
  status_label: string;
  priority: PriorityLevel;
  icon: string;
  color: string;
}

// =====================================================
// INTERFACES DE PLANTILLAS - GOAL TEMPLATES
// =====================================================

// Plantilla de meta (GoalTemplate model)
export interface GoalTemplate {
  id: number;
  name: string;
  description: string;
  goal_type: GoalType;
  suggested_amount?: string; // Decimal como string
  suggested_amount_calculated: number; // ReadOnly - calculado por usuario
  suggested_timeframe_months: number;
  icon: string;
  color: string;
  tips: string[]; // JSONField array de consejos
}

// =====================================================
// INTERFACES DE REPORTES Y ANALYTICS
// =====================================================

// Reporte de progreso general (GoalProgressReportSerializer)
export interface GoalProgressReport {
  total_goals: number;
  active_goals: number;
  completed_goals: number;
  overdue_goals: number;
  total_target_amount: string; // Decimal como string
  total_current_amount: string; // Decimal como string
  overall_progress: number; // Float percentage
  monthly_contributions: string; // Decimal como string
  goals_on_track: number;
}

// Analytics de meta específica (GoalAnalyticsSerializer)
export interface GoalAnalytics {
  goal_id: number;
  goal_title: string;
  progress_trend: ProgressTrendItem[];
  monthly_contributions: MonthlyContributionItem[];
  projected_completion_date: string; // ISO date
  is_on_track: boolean;
  recommended_monthly_amount: string; // Decimal como string
  expected_progress?: number; // Progreso esperado %
  actual_progress?: number; // Progreso real %
}

// Items del trend de progreso
export interface ProgressTrendItem {
  date: string; // ISO date
  progress: number; // Percentage
  amount: string; // Decimal como string
}

// Items de contribuciones mensuales
export interface MonthlyContributionItem {
  month: string; // 'YYYY-MM' format
  amount: number; // Float para gráficos
  count: number; // Número de contribuciones
}

// Dashboard completo de metas (GoalDashboardSerializer)
export interface GoalDashboard {
  summary: GoalProgressReport;
  recent_goals: FinancialGoalSummary[];
  urgent_goals: FinancialGoalSummary[];
  top_performing_goals: FinancialGoalSummary[];
  monthly_progress_chart: ChartData;
  goals_by_type_chart: ChartData;
}

// Datos para gráficos Chart.js
export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label?: string;
  data: number[];
  backgroundColor: string | string[];
  borderColor?: string;
  borderWidth?: number;
}

// =====================================================
// INTERFACES DE FORMULARIOS Y REQUESTS
// =====================================================

// Request para crear meta
export interface CreateGoalRequest {
  title: string;
  description?: string;
  goal_type: GoalType;
  target_amount: string;
  target_date: string;
  start_date?: string;
  monthly_target?: string;
  auto_contribution?: string;
  associated_account?: number;
  related_categories?: number[];
  priority?: PriorityLevel;
  is_public?: boolean;
  icon?: string;
  color?: string;
  enable_reminders?: boolean;
  reminder_frequency?: ReminderFrequency;
}

// Request para actualizar meta
export interface UpdateGoalRequest extends Partial<CreateGoalRequest> {}

// Request para crear contribución
export interface CreateContributionRequest {
  amount: string;
  contribution_type: ContributionType;
  date: string;
  from_account: number;
  related_transaction?: number;
  notes?: string;
  is_recurring?: boolean;
}

// Request para crear meta desde plantilla (GoalCreateFromTemplateSerializer)
export interface CreateGoalFromTemplateRequest {
  template_id: number;
  title?: string;
  target_amount?: string;
  target_date?: string;
  associated_account?: number;
}

// Request para crear hito
export interface CreateMilestoneRequest {
  title: string;
  description?: string;
  target_amount: string;
  target_date: string;
  icon?: string;
  order?: number;
}

// =====================================================
// INTERFACES DE CALENDARIO E INSIGHTS
// =====================================================

// Evento de calendario
export interface GoalCalendarEvent {
  date: string; // 'YYYY-MM-DD'
  type: 'goal_deadline' | 'milestone' | 'contribution';
  title: string;
  description: string;
  goal_id: number;
  status: GoalStatus;
  progress: number;
  color: string;
}

// Vista de calendario
export interface GoalCalendar {
  year: number;
  month: number;
  events: GoalCalendarEvent[];
  summary: {
    goals_due_this_month: number;
    urgent_goals: number;
  };
}

// Insight inteligente
export interface GoalInsight {
  type: 'warning' | 'info' | 'success' | 'suggestion';
  title: string;
  message: string;
  action: string; // Action ID para el frontend
  priority: 'low' | 'medium' | 'high';
}

// Respuesta de insights
export interface GoalInsights {
  insights: GoalInsight[];
  generated_at: string; // ISO datetime
}

// =====================================================
// INTERFACES DE FILTROS (desde filters.py)
// =====================================================

// Filtros de metas financieras (FinancialGoalFilter)
export interface GoalFilters extends BaseFilterParams {
  // Búsqueda de texto
  title?: string;
  description?: string;
  
  // Selección
  goal_type?: GoalType | GoalType[];
  status?: GoalStatus | GoalStatus[];
  priority?: PriorityLevel | PriorityLevel[];
  
  // Rangos de montos
  min_target_amount?: number;
  max_target_amount?: number;
  min_current_amount?: number;
  max_current_amount?: number;
  
  // Fechas
  start_date_after?: string;
  start_date_before?: string;
  target_date_after?: string;
  target_date_before?: string;
  
  // Relaciones
  associated_account?: number;
  bank?: string;
  related_category?: number;
  
  // Progreso
  min_progress?: number; // 0-100
  max_progress?: number; // 0-100
  
  // Tiempo restante
  days_remaining_less_than?: number;
  days_remaining_more_than?: number;
  
  // Booleanos
  is_overdue?: boolean;
  has_contributions?: boolean;
  is_on_track?: boolean;
  enable_reminders?: boolean;
}

// Filtros de contribuciones (GoalContributionFilter)
export interface ContributionFilters extends BaseFilterParams {
  // Relaciones
  goal?: number;
  goal_title?: string;
  from_account?: number;
  bank?: string;
  
  // Montos
  min_amount?: number;
  max_amount?: number;
  
  // Fechas
  date_after?: string;
  date_before?: string;
  year?: number;
  month?: number;
  
  // Tipo
  contribution_type?: ContributionType;
  
  // Booleanos
  is_recurring?: boolean;
  has_transaction?: boolean;
  
  // Búsqueda
  notes?: string;
}

// =====================================================
// INTERFACES DE RESPUESTAS DE API
// =====================================================

// Respuesta de acción en meta
export interface GoalActionResponse {
  message: string;
  status?: GoalStatus;
  completed_at?: string;
  goal_progress?: number;
  goal_current_amount?: number;
  goal_remaining_amount?: number;
}

// Respuesta de agregar contribución
export interface AddContributionResponse {
  message: string;
  contribution: GoalContribution;
  goal_progress: number;
  goal_current_amount: number;
  goal_remaining_amount: number;
}

// Respuesta de contribuciones con estadísticas
export interface GoalContributionsResponse {
  contributions: GoalContribution[];
  statistics: {
    total_amount: number;
    contribution_count: number;
    average_contribution: number;
  };
}

// Respuesta de summary de metas
export interface GoalSummaryResponse {
  total_goals: number;
  active_goals: number;
  completed_goals: number;
  total_saved: number;
  total_target: number;
  next_to_complete?: FinancialGoalSummary;
}

// =====================================================
// INTERFACES DE UI Y FORMULARIOS
// =====================================================

// Estado de formulario de meta
export interface GoalFormState {
  title: string;
  description: string;
  goal_type: GoalType;
  target_amount: string;
  target_date: string;
  start_date: string;
  monthly_target: string;
  auto_contribution: string;
  associated_account?: number;
  related_categories: number[];
  priority: PriorityLevel;
  is_public: boolean;
  icon: string;
  color: string;
  enable_reminders: boolean;
  reminder_frequency: ReminderFrequency;
}

// Estado de formulario de contribución
export interface ContributionFormState {
  amount: string;
  contribution_type: ContributionType;
  date: string;
  from_account: number;
  related_transaction?: number;
  notes: string;
  is_recurring: boolean;
}

// Estado de formulario de hito
export interface MilestoneFormState {
  title: string;
  description: string;
  target_amount: string;
  target_date: string;
  icon: string;
  order: number;
}

// Opciones para selector de metas
export interface GoalSelectOption {
  value: number;
  label: string;
  goal_type: GoalType;
  progress: number;
  status: GoalStatus;
  icon: string;
  color: string;
}

// =====================================================
// INTERFACES DE PRESETS Y UTILIDADES
// =====================================================

// Presets comunes de filtros
export interface GoalFilterPresets {
  ALL_ACTIVE: GoalFilters;
  URGENT: GoalFilters;
  ALMOST_COMPLETE: GoalFilters;
  OVERDUE: GoalFilters;
  SAVINGS_GOALS: GoalFilters;
  HIGH_PRIORITY: GoalFilters;
  THIS_MONTH: GoalFilters;
  NEED_ATTENTION: GoalFilters;
}

// Métricas calculadas para UI
export interface GoalMetrics {
  progress_percentage: number;
  remaining_amount: string;
  days_remaining: number;
  suggested_monthly: string;
  is_on_track: boolean;
  completion_probability: number; // 0-100
}

// =====================================================
// INTERFACES DE ACCIONES BULK Y OPERACIONES
// =====================================================

// Request para operaciones bulk
export interface BulkGoalOperation {
  goal_ids: number[];
  action: 'pause' | 'resume' | 'delete' | 'complete' | 'update_priority';
  params?: Record<string, any>;
}

// Resultado de operación bulk
export interface BulkOperationResult {
  success_count: number;
  error_count: number;
  errors: Array<{
    goal_id: number;
    error: string;
  }>;
}

// =====================================================
// CONSTANTES PARA UI
// =====================================================

// Iconos por tipo de meta
export const GOAL_TYPE_ICONS: Record<GoalType, string> = {
  savings: 'piggy-bank',
  expense_reduction: 'trending-down',
  income_increase: 'trending-up',
  debt_payment: 'credit-card',
  emergency_fund: 'shield',
  investment: 'bar-chart-3',
  purchase: 'shopping-cart',
  vacation: 'plane',
  education: 'graduation-cap',
  retirement: 'calendar',
  other: 'target',
};

// Colores por prioridad
export const PRIORITY_COLORS: Record<PriorityLevel, string> = {
  low: '#10b981',      // green
  medium: '#f59e0b',   // yellow
  high: '#ef4444',     // red
  critical: '#dc2626', // dark red
};

// Colores por estado
export const STATUS_COLORS: Record<GoalStatus, string> = {
  active: '#3b82f6',    // blue
  paused: '#6b7280',    // gray
  completed: '#10b981', // green
  cancelled: '#ef4444', // red
  overdue: '#dc2626',   // dark red
};

// =====================================================
// CONSTANTES DE VALIDACIÓN
// =====================================================

export const GOAL_VALIDATION = {
  TITLE: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 200,
  },
  DESCRIPTION: {
    MAX_LENGTH: 1000,
  },
  TARGET_AMOUNT: {
    MIN: 1,
    MAX: 999999999.99,
  },
  MONTHLY_TARGET: {
    MIN: 0.01,
    MAX: 999999.99,
  },
} as const;

// =====================================================
// HELPERS Y UTILIDADES
// =====================================================

// Helper para validar tipo de meta
export const isValidGoalType = (type: string): type is GoalType => {
  return Object.keys(GOAL_TYPES).includes(type);
};

// Helper para validar estado
export const isValidGoalStatus = (status: string): status is GoalStatus => {
  return Object.keys(GOAL_STATUS).includes(status);
};

// Helper para validar prioridad
export const isValidPriority = (priority: string): priority is PriorityLevel => {
  return Object.keys(PRIORITY_LEVELS).includes(priority);
};

// Helper para obtener color por tipo
export const getGoalTypeColor = (goalType: GoalType): string => {
  const colorMap: Record<GoalType, string> = {
    savings: '#10b981',
    expense_reduction: '#ef4444',
    income_increase: '#3b82f6',
    debt_payment: '#f59e0b',
    emergency_fund: '#8b5cf6',
    investment: '#06b6d4',
    purchase: '#f97316',
    vacation: '#ec4899',
    education: '#84cc16',
    retirement: '#6366f1',
    other: '#6b7280',
  };
  return colorMap[goalType] || '#6b7280';
};

// Helper para calcular urgencia
export const calculateGoalUrgency = (goal: FinancialGoalSummary): 'low' | 'medium' | 'high' => {
  if (goal.days_remaining <= 7) return 'high';
  if (goal.days_remaining <= 30) return 'medium';
  return 'low';
};

// Helper para formatear progreso como texto
export const formatProgressText = (goal: FinancialGoalSummary): string => {
  const progress = Math.round(goal.progress_percentage);
  return `${progress}% (S/.${goal.current_amount} de S/.${goal.target_amount})`;
};

// =====================================================
// TYPES PARA HOOKS Y ESTADO
// =====================================================

// Estado de hook de metas
export interface UseGoalsState {
  goals: FinancialGoal[];
  summary: FinancialGoalSummary[];
  dashboard?: GoalDashboard;
  loading: boolean;
  error: string | null;
  filters: GoalFilters;
  pagination: {
    page: number;
    totalPages: number;
    totalCount: number;
  };
}

// Estado de hook de contribuciones
export interface UseContributionsState {
  contributions: GoalContribution[];
  statistics?: GoalContributionsResponse['statistics'];
  loading: boolean;
  error: string | null;
  filters: ContributionFilters;
}

// Estado de hook de plantillas
export interface UseTemplatesState {
  templates: GoalTemplate[];
  byCategory: Record<GoalType, GoalTemplate[]>;
  loading: boolean;
  error: string | null;
}

// =====================================================
// EXPORT TYPES PARA FACILITAR USO
// =====================================================

// Re-export de tipos principales para importación fácil
export type {
  FinancialGoal as Goal,
  FinancialGoalSummary as GoalSummary,
  GoalContribution as Contribution,
  GoalTemplate as Template,
  GoalMilestone as Milestone,
  GoalDashboard as Dashboard,
  GoalAnalytics as Analytics,
  GoalInsights as Insights,
};