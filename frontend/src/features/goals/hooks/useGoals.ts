import { useState, useEffect, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { goalsApi } from '../services/goalsApi';
import { 
  FinancialGoal, 
  FinancialGoalSummary,
  GoalContribution, 
  CreateGoalRequest, 
  UpdateGoalRequest,
  GoalDashboard,
  GoalSummary,
  GoalCalendarEvent,
  GoalInsight,
  GoalAnalytics
} from '../types/goals.types';
import { ApiError } from '@/types/api.types';

// =====================================================
// TIPOS PARA EL HOOK
// =====================================================
export interface UseGoalsOptions {
  enabled?: boolean;
  refetchInterval?: number;
  initialFilters?: GoalFilters;
}

export interface GoalFilters {
  status?: 'active' | 'paused' | 'completed' | 'cancelled' | 'overdue';
  goal_type?: string;
  priority?: 'low' | 'medium' | 'high' | 'critical';
  search?: string;
  start_date?: string;
  end_date?: string;
}

export interface UseGoalsReturn {
  // Estados principales
  goals: FinancialGoalSummary[];
  goal: FinancialGoal | null;
  loading: boolean;
  error: ApiError | null;
  
  // Acciones CRUD
  createGoal: (goalData: CreateGoalRequest) => Promise<FinancialGoal>;
  updateGoal: (id: number, updates:  UpdateGoalRequest) => Promise<FinancialGoal>;
  deleteGoal: (id: number) => Promise<void>;
  getGoal: (id: number) => Promise<FinancialGoal>;
  
  // Acciones específicas de metas
  pauseGoal: (id: number) => Promise<void>;
  resumeGoal: (id: number) => Promise<void>;
  completeGoal: (id: number) => Promise<void>;
  addContribution: (goalId: number, contribution: Omit<GoalContribution, 'id' | 'goal' | 'user' | 'created_at'>) => Promise<void>;
  
  // Dashboard y análisis
  dashboard: GoalDashboard | null;
  summary: GoalSummary | null;
  analytics: (goalId: number) => Promise<GoalAnalytics>;
  calendar: (year?: number, month?: number) => Promise<GoalCalendarEvent[]>;
  insights: () => Promise<GoalInsight[]>;
  
  // Utilidades
  refetch: () => Promise<void>;
  filters: GoalFilters;
  setFilters: (filters: Partial<GoalFilters>) => void;
  
  // Estados de mutaciones
  isCreating: boolean;
  isUpdating: boolean;
  isDeleting: boolean;
}

// =====================================================
// HOOK PRINCIPAL - useGoals
// =====================================================
export const useGoals = (options: UseGoalsOptions = {}): UseGoalsReturn => {
  const queryClient = useQueryClient();
  const { enabled = true, refetchInterval, initialFilters = {} } = options;
  
  // Estados locales
  const [filters, setFilters] = useState<GoalFilters>(initialFilters);
  const [goal, setGoal] = useState<FinancialGoal | null>(null);

  // =====================================================
  // QUERIES - CONSULTAS PRINCIPALES
  // =====================================================
  
  // Query principal - Lista de metas
  const {
    data: goals = [],
    isLoading: goalsLoading,
    error: goalsError,
    refetch: refetchGoals
  } = useQuery({
    queryKey: ['goals', 'list', filters],
    queryFn: () => goalsApi.getGoals(filters),
    enabled,
    refetchInterval,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });

  // Query Dashboard
  const {
    data: dashboard,
    isLoading: dashboardLoading,
    error: dashboardError
  } = useQuery({
    queryKey: ['goals', 'dashboard'],
    queryFn: goalsApi.getDashboard,
    enabled,
    staleTime: 10 * 60 * 1000, // 10 minutos
  });

  // Query Summary
  const {
    data: summary,
    isLoading: summaryLoading,
    error: summaryError
  } = useQuery({
    queryKey: ['goals', 'summary'],
    queryFn: goalsApi.getSummary,
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });

  // =====================================================
  // MUTATIONS - OPERACIONES CRUD
  // =====================================================
  
  // Crear meta
  const createMutation = useMutation({
    mutationFn: goalsApi.createGoal,
    onSuccess: (newGoal) => {
      // Invalidar cache relevantes
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      
      // Actualizar cache local optimísticamente
      queryClient.setQueryData(
        ['goals', 'list', filters],
        (oldGoals: FinancialGoalSummary[] = []) => [...oldGoals, newGoal]
      );
    },
  });

  // Actualizar meta
  const updateMutation = useMutation({
    mutationFn: ({ id, updates }: { id: number; updates:  UpdateGoalRequest }) =>
      goalsApi.updateGoal(id, updates),
    onSuccess: (updatedGoal, { id }) => {
      // Invalidar cache
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      
      // Actualizar item específico en cache
      queryClient.setQueryData(['goals', 'detail', id], updatedGoal);
      
      // Actualizar meta actual si coincide
      if (goal?.id === id) {
        setGoal(updatedGoal);
      }
    },
  });

  // Eliminar meta
  const deleteMutation = useMutation({
    mutationFn: goalsApi.deleteGoal,
    onSuccess: (_, deletedId) => {
      // Invalidar cache
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      
      // Remover de cache local
      queryClient.setQueryData(
        ['goals', 'list', filters],
        (oldGoals: FinancialGoalSummary[] = []) =>
          oldGoals.filter(goal => goal.id !== deletedId)
      );
      
      // Limpiar meta actual si es la eliminada
      if (goal?.id === deletedId) {
        setGoal(null);
      }
    },
  });

  // =====================================================
  // MUTATIONS - ACCIONES ESPECÍFICAS
  // =====================================================
  
  // Pausar meta
  const pauseMutation = useMutation({
    mutationFn: goalsApi.pauseGoal,
    onSuccess: (_, goalId) => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      
      // Actualizar estado local
      queryClient.setQueryData(
        ['goals', 'list', filters],
        (oldGoals: FinancialGoalSummary[] = []) =>
          oldGoals.map(goal => 
            goal.id === goalId 
              ? { ...goal, status: 'paused', status_label: 'Pausada' }
              : goal
          )
      );
    },
  });

  // Reanudar meta
  const resumeMutation = useMutation({
    mutationFn: goalsApi.resumeGoal,
    onSuccess: (_, goalId) => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      
      queryClient.setQueryData(
        ['goals', 'list', filters],
        (oldGoals: FinancialGoalSummary[] = []) =>
          oldGoals.map(goal => 
            goal.id === goalId 
              ? { ...goal, status: 'active', status_label: 'Activa' }
              : goal
          )
      );
    },
  });

  // Completar meta
  const completeMutation = useMutation({
    mutationFn: goalsApi.completeGoal,
    onSuccess: (_, goalId) => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      
      queryClient.setQueryData(
        ['goals', 'list', filters],
        (oldGoals: FinancialGoalSummary[] = []) =>
          oldGoals.map(goal => 
            goal.id === goalId 
              ? { ...goal, status: 'completed', status_label: 'Completada', progress_percentage: 100 }
              : goal
          )
      );
    },
  });

  // Agregar contribución
  const contributionMutation = useMutation({
    mutationFn: ({ goalId, contribution }: { goalId: number; contribution: Omit<GoalContribution, 'id' | 'goal' | 'user' | 'created_at'> }) =>
      goalsApi.addContribution(goalId, contribution),
    onSuccess: (response, { goalId }) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      queryClient.invalidateQueries({ queryKey: ['goals', 'contributions', goalId] });
      
      // Actualizar progreso en cache local si es posible
      if (response.goal_current_amount && response.goal_progress) {
        queryClient.setQueryData(
          ['goals', 'list', filters],
          (oldGoals: FinancialGoalSummary[] = []) =>
            oldGoals.map(goal => 
              goal.id === goalId 
                ? { 
                    ...goal, 
                    current_amount: response.goal_current_amount,
                    progress_percentage: response.goal_progress,
                    remaining_amount: response.goal_remaining_amount
                  }
                : goal
            )
        );
      }
    },
  });

  // =====================================================
  // FUNCIONES PÚBLICAS
  // =====================================================
  
  // Obtener meta específica
  const getGoal = useCallback(async (id: number): Promise<FinancialGoal> => {
    const cachedGoal = queryClient.getQueryData(['goals', 'detail', id]);
    
    if (cachedGoal) {
      const goalData = cachedGoal as FinancialGoal;
      setGoal(goalData);
      return goalData;
    }

    try {
      const goalData = await goalsApi.getGoal(id);
      
      // Guardar en cache
      queryClient.setQueryData(['goals', 'detail', id], goalData);
      setGoal(goalData);
      
      return goalData;
    } catch (error) {
      console.error('Error al obtener meta:', error);
      throw error;
    }
  }, [queryClient]);

  // Obtener análisis de meta específica
  const analytics = useCallback(async (goalId: number): Promise<GoalAnalytics> => {
    try {
      const analyticsData = await goalsApi.getAnalytics(goalId);
      
      // Guardar en cache temporal
      queryClient.setQueryData(
        ['goals', 'analytics', goalId], 
        analyticsData,
        { staleTime: 15 * 60 * 1000 } // 15 minutos
      );
      
      return analyticsData;
    } catch (error) {
      console.error('Error al obtener analytics:', error);
      throw error;
    }
  }, [queryClient]);

  // Obtener calendario
  const calendar = useCallback(async (year?: number, month?: number): Promise<GoalCalendarEvent[]> => {
    try {
      const calendarData = await goalsApi.getCalendar(year, month);
      
      const cacheKey = ['goals', 'calendar', year || new Date().getFullYear(), month || new Date().getMonth() + 1];
      queryClient.setQueryData(cacheKey, calendarData);
      
      return calendarData.events;
    } catch (error) {
      console.error('Error al obtener calendario:', error);
      throw error;
    }
  }, [queryClient]);

  // Obtener insights
  const insights = useCallback(async (): Promise<GoalInsight[]> => {
    try {
      const insightsData = await goalsApi.getInsights();
      
      queryClient.setQueryData(
        ['goals', 'insights'], 
        insightsData,
        { staleTime: 30 * 60 * 1000 } // 30 minutos
      );
      
      return insightsData.insights;
    } catch (error) {
      console.error('Error al obtener insights:', error);
      throw error;
    }
  }, [queryClient]);

  // Refetch general
  const refetch = useCallback(async () => {
    await Promise.all([
      refetchGoals(),
      queryClient.invalidateQueries({ queryKey: ['goals', 'dashboard'] }),
      queryClient.invalidateQueries({ queryKey: ['goals', 'summary'] })
    ]);
  }, [refetchGoals, queryClient]);

  // Actualizar filtros con debounce
  const setFiltersDebounced = useCallback((newFilters: Partial<GoalFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  // =====================================================
  // ESTADOS COMPUTADOS
  // =====================================================
  
  const loading = useMemo(() => 
    goalsLoading || dashboardLoading || summaryLoading,
    [goalsLoading, dashboardLoading, summaryLoading]
  );

  const error = useMemo(() => 
    goalsError || dashboardError || summaryError,
    [goalsError, dashboardError, summaryError]
  );

  // =====================================================
  // RETURN DEL HOOK
  // =====================================================
  return {
    // Estados principales
    goals,
    goal,
    loading,
    error: error as ApiError,
    
    // Acciones CRUD
    createGoal: createMutation.mutateAsync,
    updateGoal: useCallback(
      (id: number, updates:  UpdateGoalRequest) => 
        updateMutation.mutateAsync({ id, updates }),
      [updateMutation]
    ),
    deleteGoal: deleteMutation.mutateAsync,
    getGoal,
    
    // Acciones específicas
    pauseGoal: pauseMutation.mutateAsync,
    resumeGoal: resumeMutation.mutateAsync,
    completeGoal: completeMutation.mutateAsync,
    addContribution: useCallback(
      (goalId: number, contribution: Omit<GoalContribution, 'id' | 'goal' | 'user' | 'created_at'>) =>
        contributionMutation.mutateAsync({ goalId, contribution }),
      [contributionMutation]
    ),
    
    // Dashboard y análisis
    dashboard: dashboard || null,
    summary: summary || null,
    analytics,
    calendar,
    insights,
    
    // Utilidades
    refetch,
    filters,
    setFilters: setFiltersDebounced,
    
    // Estados de mutaciones
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
};

// =====================================================
// HOOK SIMPLIFICADO PARA COMPONENTES BÁSICOS
// =====================================================
export const useGoalsSimple = () => {
  const {
    goals,
    loading,
    error,
    summary,
    createGoal,
    updateGoal,
    deleteGoal
  } = useGoals({
    enabled: true,
    initialFilters: { status: 'active' }
  });

  return {
    goals,
    loading,
    error,
    summary,
    createGoal,
    updateGoal,
    deleteGoal
  };
};

export default useGoals;