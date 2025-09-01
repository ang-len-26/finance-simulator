// =====================================================
// GOALS API SERVICES - Servicios completos para Goals
// Rama 5 - 100% basado en backend real de goals
// =====================================================

import apiClient from '@/services/api/client';
import { GOALS_ENDPOINTS, buildUrlWithParams, buildGoalFilters, buildContributionFilters } from '@/services/api/endpoints';
import { PaginatedResponse } from '@/types/api.types';
import {
  GoalType,
  FinancialGoal,
  FinancialGoalSummary,
  GoalContribution,
  GoalTemplate,
  GoalMilestone,
  GoalDashboard,
  GoalAnalytics,
  GoalCalendar,
  GoalInsights,
  GoalSummaryResponse,
  GoalContributionsResponse,
  CreateGoalRequest,
  UpdateGoalRequest,
  CreateContributionRequest,
  CreateGoalFromTemplateRequest,
  CreateMilestoneRequest,
  GoalActionResponse,
  AddContributionResponse,
  GoalFilters,
  ContributionFilters,
} from '@/features/goals/types/goals.types';

// =====================================================
// SERVICIOS PRINCIPALES - METAS FINANCIERAS
// =====================================================

export const goalsApi = {
  // ✅ CRUD básico de metas
  async getGoals(filters?: GoalFilters): Promise<PaginatedResponse<FinancialGoalSummary>> {
    const cleanFilters = filters ? buildGoalFilters(filters) : {};
    const url = buildUrlWithParams(GOALS_ENDPOINTS.GOALS, cleanFilters);
    return apiClient.get<PaginatedResponse<FinancialGoalSummary>>(url);
  },

  async getGoal(id: number): Promise<FinancialGoal> {
    return apiClient.get<FinancialGoal>(GOALS_ENDPOINTS.GOAL_DETAIL(id));
  },

  async createGoal(goalData: CreateGoalRequest): Promise<FinancialGoal> {
    return apiClient.post<FinancialGoal>(GOALS_ENDPOINTS.GOALS, goalData);
  },

  async updateGoal(id: number, goalData: UpdateGoalRequest): Promise<FinancialGoal> {
    return apiClient.patch<FinancialGoal>(GOALS_ENDPOINTS.GOAL_DETAIL(id), goalData);
  },

  async deleteGoal(id: number): Promise<void> {
    return apiClient.delete<void>(GOALS_ENDPOINTS.GOAL_DETAIL(id));
  },

  // ✅ Dashboard y resúmenes
  async getDashboard(): Promise<GoalDashboard> {
    return apiClient.get<GoalDashboard>(GOALS_ENDPOINTS.GOALS_DASHBOARD);
  },

  async getSummary(): Promise<GoalSummaryResponse> {
    return apiClient.get<GoalSummaryResponse>(GOALS_ENDPOINTS.GOALS_SUMMARY);
  },

  // ✅ Acciones específicas de metas
  async pauseGoal(id: number): Promise<GoalActionResponse> {
    return apiClient.post<GoalActionResponse>(GOALS_ENDPOINTS.GOAL_PAUSE(id));
  },

  async resumeGoal(id: number): Promise<GoalActionResponse> {
    return apiClient.post<GoalActionResponse>(GOALS_ENDPOINTS.GOAL_RESUME(id));
  },

  async completeGoal(id: number): Promise<GoalActionResponse> {
    return apiClient.post<GoalActionResponse>(GOALS_ENDPOINTS.GOAL_COMPLETE(id));
  },

  // ✅ Analytics de meta específica
  async getGoalAnalytics(id: number): Promise<GoalAnalytics> {
    return apiClient.get<GoalAnalytics>(GOALS_ENDPOINTS.GOAL_ANALYTICS(id));
  },

  // ✅ Contribuciones de meta específica
  async getGoalContributions(
    id: number, 
    filters?: { start_date?: string; end_date?: string }
  ): Promise<GoalContributionsResponse> {
    const url = buildUrlWithParams(GOALS_ENDPOINTS.GOAL_CONTRIBUTIONS(id), filters || {});
    return apiClient.get<GoalContributionsResponse>(url);
  },

  // ✅ Agregar contribución a meta
  async addContribution(
    goalId: number, 
    contributionData: CreateContributionRequest
  ): Promise<AddContributionResponse> {
    return apiClient.post<AddContributionResponse>(
      GOALS_ENDPOINTS.GOAL_ADD_CONTRIBUTION(goalId), 
      contributionData
    );
  },

  // ✅ Agregar hito a meta
  async addMilestone(goalId: number, milestoneData: CreateMilestoneRequest): Promise<GoalMilestone> {
    return apiClient.post<GoalMilestone>(
      GOALS_ENDPOINTS.GOAL_ADD_MILESTONE(goalId), 
      milestoneData
    );
  },
};

// =====================================================
// SERVICIOS DE CONTRIBUCIONES
// =====================================================

export const contributionsApi = {
  // ✅ CRUD de contribuciones
  async getContributions(filters?: ContributionFilters): Promise<PaginatedResponse<GoalContribution>> {
    const cleanFilters = filters ? buildContributionFilters(filters) : {};
    const url = buildUrlWithParams(GOALS_ENDPOINTS.CONTRIBUTIONS, cleanFilters);
    return apiClient.get<PaginatedResponse<GoalContribution>>(url);
  },

  async getContribution(id: number): Promise<GoalContribution> {
    return apiClient.get<GoalContribution>(GOALS_ENDPOINTS.CONTRIBUTION_DETAIL(id));
  },

  async createContribution(contributionData: CreateContributionRequest): Promise<GoalContribution> {
    return apiClient.post<GoalContribution>(GOALS_ENDPOINTS.CONTRIBUTIONS, contributionData);
  },

  async updateContribution(id: number, contributionData: Partial<CreateContributionRequest>): Promise<GoalContribution> {
    return apiClient.patch<GoalContribution>(GOALS_ENDPOINTS.CONTRIBUTION_DETAIL(id), contributionData);
  },

  async deleteContribution(id: number): Promise<void> {
    return apiClient.delete<void>(GOALS_ENDPOINTS.CONTRIBUTION_DETAIL(id));
  },
};

// =====================================================
// SERVICIOS DE PLANTILLAS
// =====================================================

export const templatesApi = {
  // ✅ Obtener plantillas
  async getTemplates(): Promise<GoalTemplate[]> {
    return apiClient.get<GoalTemplate[]>(GOALS_ENDPOINTS.TEMPLATES);
  },

  async getTemplate(id: number): Promise<GoalTemplate> {
    return apiClient.get<GoalTemplate>(GOALS_ENDPOINTS.TEMPLATE_DETAIL(id));
  },

  // ✅ Plantillas agrupadas por categoría
  async getTemplatesByCategory(): Promise<Record<string, GoalTemplate[]>> {
    return apiClient.get<Record<string, GoalTemplate[]>>(GOALS_ENDPOINTS.TEMPLATES_BY_CATEGORY);
  },

  // ✅ Crear meta desde plantilla
  async createGoalFromTemplate(
    templateId: number, 
    data: Omit<CreateGoalFromTemplateRequest, 'template_id'>
  ): Promise<FinancialGoal> {
    return apiClient.post<FinancialGoal>(
      GOALS_ENDPOINTS.TEMPLATE_CREATE_GOAL(templateId), 
      data
    );
  },

  // ✅ Setup plantillas predeterminadas
  async setupDefaultTemplates(): Promise<{ message: string; total_templates: number }> {
    return apiClient.post<{ message: string; total_templates: number }>(
      GOALS_ENDPOINTS.SETUP_TEMPLATES
    );
  },
};

// =====================================================
// SERVICIOS DE UTILIDADES
// =====================================================

export const goalUtilitiesApi = {
  // ✅ Calendario de metas
  async getGoalsCalendar(year?: number, month?: number): Promise<GoalCalendar> {
    const params: Record<string, any> = {};
    if (year) params.year = year;
    if (month) params.month = month;
    
    const url = buildUrlWithParams(GOALS_ENDPOINTS.GOALS_CALENDAR, params);
    return apiClient.get<GoalCalendar>(url);
  },

  // ✅ Insights inteligentes
  async getGoalsInsights(): Promise<GoalInsights> {
    return apiClient.get<GoalInsights>(GOALS_ENDPOINTS.GOALS_INSIGHTS);
  },
};

// =====================================================
// SERVICIOS ESPECIALIZADOS Y COMBINADOS
// =====================================================

export const goalQueriesApi = {
  // 🔥 Queries especializadas usando filtros del backend

  // Metas urgentes (vencen en 30 días)
  async getUrgentGoals(): Promise<FinancialGoalSummary[]> {
    const filters: GoalFilters = {
      status: 'active',
      days_remaining_less_than: 30,
      ordering: 'target_date'
    };
    const response = await goalsApi.getGoals(filters);
    return response.results;
  },

  // Metas casi completas (90%+)
  async getAlmostCompleteGoals(): Promise<FinancialGoalSummary[]> {
    const filters: GoalFilters = {
      status: 'active',
      min_progress: 90,
      ordering: '-progress_percentage'
    };
    const response = await goalsApi.getGoals(filters);
    return response.results;
  },

  // Metas vencidas
  async getOverdueGoals(): Promise<FinancialGoalSummary[]> {
    const filters: GoalFilters = {
      is_overdue: true,
      ordering: 'target_date'
    };
    const response = await goalsApi.getGoals(filters);
    return response.results;
  },

  // Metas de alta prioridad
  async getHighPriorityGoals(): Promise<FinancialGoalSummary[]> {
    const filters: GoalFilters = {
      priority: ['high', 'critical'],
      status: 'active',
      ordering: '-priority'
    };
    const response = await goalsApi.getGoals(filters);
    return response.results;
  },

  // Metas por tipo específico
  async getGoalsByType(goalType: GoalType | GoalType[]): Promise<FinancialGoalSummary[]> {
    const filters: GoalFilters = {
      goal_type: goalType,
      ordering: '-created_at'
    };
    const response = await goalsApi.getGoals(filters);
    return response.results;
  },

  // Metas que necesitan atención (progreso lento)
  async getGoalsNeedingAttention(): Promise<FinancialGoalSummary[]> {
    const filters: GoalFilters = {
      status: 'active',
      is_on_track: false,
      ordering: 'target_date'
    };
    const response = await goalsApi.getGoals(filters);
    return response.results;
  },

  // Contribuciones recientes (últimos 30 días)
  async getRecentContributions(): Promise<GoalContribution[]> {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    const filters: ContributionFilters = {
      date_after: thirtyDaysAgo.toISOString().split('T')[0],
      ordering: '-date'
    };
    const response = await contributionsApi.getContributions(filters);
    return response.results;
  },

  // Contribuciones por meta y período
  async getContributionsByGoalAndPeriod(
    goalId: number, 
    startDate: string, 
    endDate: string
  ): Promise<GoalContribution[]> {
    const filters: ContributionFilters = {
      goal: goalId,
      date_after: startDate,
      date_before: endDate,
      ordering: '-date'
    };
    const response = await contributionsApi.getContributions(filters);
    return response.results;
  },

  // Contribuciones automáticas
  async getAutomaticContributions(): Promise<GoalContribution[]> {
    const filters: ContributionFilters = {
      contribution_type: 'automatic',
      ordering: '-date'
    };
    const response = await contributionsApi.getContributions(filters);
    return response.results;
  },
};

// =====================================================
// SERVICIOS DE VALIDACIÓN Y CÁLCULOS
// =====================================================

export const goalCalculationsApi = {
  // Validar si se puede crear una contribución
  async validateContribution(
    goalId: number, 
    amount: string, 
    fromAccountId: number
  ): Promise<{ isValid: boolean; errors: string[] }> {
    try {
      // Obtener meta y cuenta
      const [goal, account] = await Promise.all([
        goalsApi.getGoal(goalId),
        apiClient.get(`/accounts/${fromAccountId}/`)
      ]);

      const errors: string[] = [];
      const numAmount = parseFloat(amount);

      // Validaciones
      if (numAmount <= 0) {
        errors.push('El monto debe ser positivo');
      }

      if (goal.status !== 'active') {
        errors.push('Solo se pueden agregar contribuciones a metas activas');
      }

      const newTotal = parseFloat(goal.current_amount) + numAmount;
      if (newTotal > parseFloat(goal.target_amount)) {
        errors.push('La contribución excede el monto objetivo de la meta');
      }

      return {
        isValid: errors.length === 0,
        errors
      };
    } catch (error) {
      return {
        isValid: false,
        errors: ['Error al validar contribución']
      };
    }
  },

  // Calcular métricas de progreso
  calculateGoalMetrics(goal: FinancialGoal | FinancialGoalSummary) {
    const targetAmount = parseFloat(goal.target_amount);
    const currentAmount = parseFloat(goal.current_amount);
    const progress = targetAmount > 0 ? (currentAmount / targetAmount) * 100 : 0;

    return {
      progress_percentage: Math.min(Math.round(progress), 100),
      remaining_amount: Math.max(targetAmount - currentAmount, 0).toFixed(2),
      is_complete: progress >= 100,
      amount_formatted: {
        current: `S/.${currentAmount.toLocaleString()}`,
        target: `S/.${targetAmount.toLocaleString()}`,
        remaining: `S/.${Math.max(targetAmount - currentAmount, 0).toLocaleString()}`
      }
    };
  },

  // Calcular contribución mensual sugerida
  calculateSuggestedMonthly(goal: FinancialGoal): string {
    const remaining = parseFloat(goal.remaining_amount);
    const daysRemaining = goal.days_remaining;
    
    if (daysRemaining <= 0) return remaining.toFixed(2);
    
    const monthsRemaining = Math.max(daysRemaining / 30, 1);
    const monthlyAmount = remaining / monthsRemaining;
    
    return monthlyAmount.toFixed(2);
  },

  // Verificar si meta está en buen camino
  isGoalOnTrack(goal: FinancialGoal): boolean {
    if (goal.days_remaining <= 0) return goal.progress_percentage >= 100;
    
    // Calcular progreso esperado basado en tiempo transcurrido
    const totalDays = new Date(goal.target_date).getTime() - new Date(goal.start_date).getTime();
    const daysPassed = totalDays - (goal.days_remaining * 24 * 60 * 60 * 1000);
    const expectedProgress = totalDays > 0 ? (daysPassed / totalDays) * 100 : 0;
    
    // Considerar en buen camino si está dentro del 15% del progreso esperado
    return goal.progress_percentage >= (expectedProgress - 15);
  }
};

// =====================================================
// SERVICIOS DE OPERACIONES BULK
// =====================================================

export const goalBulkApi = {
  // Pausar múltiples metas
  async pauseMultipleGoals(goalIds: number[]): Promise<GoalActionResponse[]> {
    const promises = goalIds.map(id => goalsApi.pauseGoal(id));
    return Promise.allSettled(promises).then(results =>
      results.map((result, index) => 
        result.status === 'fulfilled' 
          ? result.value 
          : { message: `Error en meta ${goalIds[index]}`, status: 'error' as any }
      )
    );
  },

  // Completar múltiples metas
  async completeMultipleGoals(goalIds: number[]): Promise<GoalActionResponse[]> {
    const promises = goalIds.map(id => goalsApi.completeGoal(id));
    return Promise.allSettled(promises).then(results =>
      results.map((result, index) => 
        result.status === 'fulfilled' 
          ? result.value 
          : { message: `Error en meta ${goalIds[index]}`, status: 'error' as any }
      )
    );
  },

  // Eliminar múltiples metas
  async deleteMultipleGoals(goalIds: number[]): Promise<{ success: number; errors: number }> {
    const promises = goalIds.map(async (id) => {
      try {
        await goalsApi.deleteGoal(id);
        return { success: true, id };
      } catch (error) {
        return { success: false, id, error };
      }
    });

    const results = await Promise.allSettled(promises);
    const successCount = results.filter(r => r.status === 'fulfilled' && r.value.success).length;
    const errorCount = results.length - successCount;

    return { success: successCount, errors: errorCount };
  }
};

// =====================================================
// SERVICIOS DE ESTADÍSTICAS Y REPORTES
// =====================================================

export const goalStatsApi = {
  // Estadísticas por tipo de meta
  async getStatsByType(): Promise<Record<string, { count: number; total_amount: number; avg_progress: number }>> {
    try {
      const response = await goalsApi.getGoals({ page_size: 1000 }); // Get all
      const goals = response.results;

      const stats: Record<string, { count: number; total_amount: number; avg_progress: number }> = {};

      goals.forEach(goal => {
        if (!stats[goal.goal_type]) {
          stats[goal.goal_type] = { count: 0, total_amount: 0, avg_progress: 0 };
        }

        stats[goal.goal_type].count++;
        stats[goal.goal_type].total_amount += parseFloat(goal.target_amount);
        stats[goal.goal_type].avg_progress += goal.progress_percentage;
      });

      // Calcular promedios
      Object.keys(stats).forEach(type => {
        stats[type].avg_progress = stats[type].avg_progress / stats[type].count;
      });

      return stats;
    } catch (error) {
      console.error('Error getting goal stats:', error);
      return {};
    }
  },

  // Progreso histórico de todas las metas
  async getProgressHistory(days: number = 90): Promise<Array<{ date: string; total_progress: number; total_amount: string }>> {
    try {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - days);

      // Obtener contribuciones del período
      const filters: ContributionFilters = {
        date_after: startDate.toISOString().split('T')[0],
        date_before: endDate.toISOString().split('T')[0],
        ordering: 'date'
      };

      const response = await contributionsApi.getContributions(filters);
      const contributions = response.results;

      // Agrupar por fecha y calcular totales acumulativos
      const dailyTotals: Record<string, number> = {};
      let runningTotal = 0;

      contributions.forEach(contribution => {
        const date = contribution.date;
        if (!dailyTotals[date]) {
          dailyTotals[date] = 0;
        }
        dailyTotals[date] += parseFloat(contribution.amount);
      });

      // Convertir a array ordenado
      const history: Array<{ date: string; total_progress: number; total_amount: string }> = [];
      
      Object.keys(dailyTotals).sort().forEach(date => {
        runningTotal += dailyTotals[date];
        history.push({
          date,
          total_progress: runningTotal, // Se puede mejorar con cálculo real de %
          total_amount: runningTotal.toFixed(2)
        });
      });

      return history;
    } catch (error) {
      console.error('Error getting progress history:', error);
      return [];
    }
  },

  // Top contribuidores (cuentas que más aportan)
  async getTopContributorAccounts(limit: number = 5): Promise<Array<{ account_id: number; account_name: string; total_contributed: string; contribution_count: number }>> {
    try {
      const response = await contributionsApi.getContributions({ page_size: 1000 });
      const contributions = response.results;

      // Agrupar por cuenta
      const accountStats: Record<number, { 
        name: string; 
        total: number; 
        count: number; 
      }> = {};

      contributions.forEach(contribution => {
        const accountId = contribution.from_account;
        const accountName = contribution.from_account_name;
        const amount = parseFloat(contribution.amount);

        if (!accountStats[accountId]) {
          accountStats[accountId] = { name: accountName, total: 0, count: 0 };
        }

        accountStats[accountId].total += amount;
        accountStats[accountId].count++;
      });

      // Convertir a array y ordenar por total
      return Object.entries(accountStats)
        .map(([accountId, stats]) => ({
          account_id: parseInt(accountId),
          account_name: stats.name,
          total_contributed: stats.total.toFixed(2),
          contribution_count: stats.count
        }))
        .sort((a, b) => parseFloat(b.total_contributed) - parseFloat(a.total_contributed))
        .slice(0, limit);
    } catch (error) {
      console.error('Error getting top contributors:', error);
      return [];
    }
  }
};

// =====================================================
// PRESETS DE FILTROS COMUNES
// =====================================================

export const goalFilterPresets = {
  // Metas activas
  ACTIVE_GOALS: { status: 'active', ordering: '-priority' } as GoalFilters,
  
  // Metas urgentes (vencen en 2 semanas)
  URGENT_GOALS: { 
    status: 'active', 
    days_remaining_less_than: 14,
    ordering: 'target_date' 
  } as GoalFilters,
  
  // Metas casi completas (80%+)
  ALMOST_COMPLETE: { 
    status: 'active', 
    min_progress: 80,
    ordering: '-progress_percentage' 
  } as GoalFilters,
  
  // Metas vencidas
  OVERDUE_GOALS: { 
    is_overdue: true,
    ordering: 'target_date' 
  } as GoalFilters,
  
  // Metas de ahorro
  SAVINGS_GOALS: { 
    goal_type: ['savings', 'emergency_fund'],
    status: 'active',
    ordering: '-target_amount' 
  } as GoalFilters,
  
  // Metas de alta prioridad
  HIGH_PRIORITY: { 
    priority: ['high', 'critical'],
    status: 'active',
    ordering: '-priority' 
  } as GoalFilters,
  
  // Metas del mes actual
  THIS_MONTH: {
    target_date_after: new Date().toISOString().split('T')[0],
    target_date_before: new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).toISOString().split('T')[0],
    ordering: 'target_date'
  } as GoalFilters,
  
  // Metas que necesitan atención
  NEED_ATTENTION: { 
    status: 'active',
    is_on_track: false,
    ordering: 'target_date' 
  } as GoalFilters,
};

export const contributionFilterPresets = {
  // Contribuciones del mes actual
  THIS_MONTH: {
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1,
    ordering: '-date'
  } as ContributionFilters,
  
  // Contribuciones automáticas
  AUTOMATIC: { 
    contribution_type: 'automatic',
    ordering: '-date' 
  } as ContributionFilters,
  
  // Contribuciones recurrentes
  RECURRING: { 
    is_recurring: true,
    ordering: '-date' 
  } as ContributionFilters,
  
  // Contribuciones grandes (más de 500)
  LARGE_CONTRIBUTIONS: { 
    min_amount: 500,
    ordering: '-amount' 
  } as ContributionFilters,
  
  // Últimos 30 días
  RECENT: {
    date_after: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    ordering: '-date'
  } as ContributionFilters,
};

// =====================================================
// EXPORT DE API UNIFICADA
// =====================================================

// API unificada de goals
export const goalApi = {
  // Servicios principales
  ...goalsApi,
  
  // Servicios especializados
  contributions: contributionsApi,
  templates: templatesApi,
  utilities: goalUtilitiesApi,
  queries: goalQueriesApi,
  calculations: goalCalculationsApi,
  bulk: goalBulkApi,
  stats: goalStatsApi,
  
  // Presets
  filterPresets: goalFilterPresets,
  contributionPresets: contributionFilterPresets,
};

export default goalApi;