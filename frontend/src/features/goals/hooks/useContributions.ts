import { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { goalsApi } from '../services/goalsApi';
import { 
  GoalContribution, 
  CreateContributionData,
  UpdateContributionData,
  ContributionStatistics,
  ContributionFilters
} from '../types/goals.types';
import { ApiError } from '@/types/api.types';

// =====================================================
// TIPOS PARA EL HOOK
// =====================================================
export interface UseContributionsOptions {
  goalId?: number;
  enabled?: boolean;
  refetchInterval?: number;
  initialFilters?: ContributionFilters;
}

export interface UseContributionsReturn {
  // Estados principales
  contributions: GoalContribution[];
  loading: boolean;
  error: ApiError | null;
  
  // Estadísticas
  statistics: ContributionStatistics | null;
  
  // Acciones CRUD
  createContribution: (goalId: number, data: CreateContributionData) => Promise<GoalContribution>;
  updateContribution: (id: number, updates: UpdateContributionData) => Promise<GoalContribution>;
  deleteContribution: (id: number) => Promise<void>;
  getContribution: (id: number) => Promise<GoalContribution>;
  
  // Filtros y búsqueda
  filters: ContributionFilters;
  setFilters: (filters: Partial<ContributionFilters>) => void;
  
  // Utilidades
  refetch: () => Promise<void>;
  
  // Estados de mutaciones
  isCreating: boolean;
  isUpdating: boolean;
  isDeleting: boolean;
  
  // Análisis de contribuciones
  getMonthlyTrend: (months: number) => Promise<any[]>;
  getContributionsByAccount: () => { account_name: string; total: number; count: number }[];
  getTotalsByMonth: () => { month: string; total: number; count: number }[];
  getAverageContribution: () => number;
  getLargestContribution: () => GoalContribution | null;
  getRecentContributions: (limit: number) => GoalContribution[];
}

// =====================================================
// HOOK PRINCIPAL - useContributions
// =====================================================
export const useContributions = (options: UseContributionsOptions = {}): UseContributionsReturn => {
  const queryClient = useQueryClient();
  const { 
    goalId, 
    enabled = true, 
    refetchInterval, 
    initialFilters = {} 
  } = options;
  
  // Estados locales
  const [filters, setFiltersState] = useState<ContributionFilters>(initialFilters);

  // =====================================================
  // QUERIES - CONSULTAS PRINCIPALES
  // =====================================================
  
  // Query principal - Todas las contribuciones del usuario
  const {
    data: allContributions = [],
    isLoading: allContributionsLoading,
    error: allContributionsError,
    refetch: refetchAllContributions
  } = useQuery({
    queryKey: ['contributions', 'list', filters],
    queryFn: () => goalsApi.getContributions(filters),
    enabled: enabled && !goalId, // Solo si no hay goalId específico
    refetchInterval,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });

  // Query específica - Contribuciones de una meta específica
  const {
    data: goalContributionsData,
    isLoading: goalContributionsLoading,
    error: goalContributionsError,
    refetch: refetchGoalContributions
  } = useQuery({
    queryKey: ['goals', 'contributions', goalId, filters],
    queryFn: () => goalsApi.getGoalContributions(goalId!, filters),
    enabled: enabled && !!goalId, // Solo si hay goalId específico
    refetchInterval,
    staleTime: 5 * 60 * 1000,
  });

  // =====================================================
  // MUTATIONS - OPERACIONES CRUD
  // =====================================================
  
  // Crear contribución
  const createMutation = useMutation({
    mutationFn: ({ goalId, data }: { goalId: number; data: CreateContributionData }) =>
      goalsApi.addContribution(goalId, data),
    onSuccess: (response, { goalId: mutationGoalId }) => {
      // Invalidar cache relevantes
      queryClient.invalidateQueries({ queryKey: ['contributions'] });
      queryClient.invalidateQueries({ queryKey: ['goals', 'contributions', mutationGoalId] });
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      
      // Actualizar cache local optimísticamente si es posible
      if (response.contribution) {
        if (goalId === mutationGoalId) {
          queryClient.setQueryData(
            ['goals', 'contributions', goalId, filters],
            (oldData: any) => {
              if (oldData?.contributions) {
                return {
                  ...oldData,
                  contributions: [response.contribution, ...oldData.contributions]
                };
              }
              return oldData;
            }
          );
        }
      }
    },
  });

  // Actualizar contribución
  const updateMutation = useMutation({
    mutationFn: ({ id, updates }: { id: number; updates: UpdateContributionData }) =>
      goalsApi.updateContribution(id, updates),
    onSuccess: (updatedContribution, { id }) => {
      // Invalidar cache
      queryClient.invalidateQueries({ queryKey: ['contributions'] });
      queryClient.invalidateQueries({ queryKey: ['goals', 'contributions'] });
      
      // Actualizar en cache local si es posible
      queryClient.setQueryData(['contributions', 'detail', id], updatedContribution);
    },
  });

  // Eliminar contribución
  const deleteMutation = useMutation({
    mutationFn: goalsApi.deleteContribution,
    onSuccess: (_, deletedId) => {
      // Invalidar cache
      queryClient.invalidateQueries({ queryKey: ['contributions'] });
      queryClient.invalidateQueries({ queryKey: ['goals', 'contributions'] });
      queryClient.invalidateQueries({ queryKey: ['goals'] }); // Para actualizar progreso
      
      // Remover de cache local
      if (goalId) {
        queryClient.setQueryData(
          ['goals', 'contributions', goalId, filters],
          (oldData: any) => {
            if (oldData?.contributions) {
              return {
                ...oldData,
                contributions: oldData.contributions.filter((c: GoalContribution) => c.id !== deletedId)
              };
            }
            return oldData;
          }
        );
      }
    },
  });

  // =====================================================
  // FUNCIONES PÚBLICAS
  // =====================================================
  
  // Obtener contribución específica
  const getContribution = useCallback(async (id: number): Promise<GoalContribution> => {
    const cachedContribution = queryClient.getQueryData(['contributions', 'detail', id]);
    
    if (cachedContribution) {
      return cachedContribution as GoalContribution;
    }

    try {
      const contribution = await goalsApi.getContribution(id);
      
      // Guardar en cache
      queryClient.setQueryData(['contributions', 'detail', id], contribution);
      
      return contribution;
    } catch (error) {
      console.error('Error al obtener contribución:', error);
      throw error;
    }
  }, [queryClient]);

  // Refetch general
  const refetch = useCallback(async () => {
    if (goalId) {
      await refetchGoalContributions();
    } else {
      await refetchAllContributions();
    }
  }, [goalId, refetchGoalContributions, refetchAllContributions]);

  // Actualizar filtros
  const setFilters = useCallback((newFilters: Partial<ContributionFilters>) => {
    setFiltersState(prev => ({ ...prev, ...newFilters }));
  }, []);

  // =====================================================
  // ANÁLISIS Y UTILIDADES
  // =====================================================
  
  // Obtener tendencia mensual
  const getMonthlyTrend = useCallback(async (months: number = 6) => {
    try {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setMonth(startDate.getMonth() - months);
      
      const trendData = await goalsApi.getContributionsTrend({
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        goal_id: goalId
      });
      
      return trendData;
    } catch (error) {
      console.error('Error al obtener tendencia:', error);
      return [];
    }
  }, [goalId]);

  // Estados computados basados en las contribuciones actuales
  const contributions = useMemo(() => {
    if (goalId && goalContributionsData) {
      return goalContributionsData.contributions || [];
    }
    return allContributions || [];
  }, [goalId, goalContributionsData, allContributions]);

  const statistics = useMemo(() => {
    if (goalId && goalContributionsData) {
      return goalContributionsData.statistics || null;
    }
    
    // Calcular estadísticas para todas las contribuciones
    if (allContributions && allContributions.length > 0) {
      const total = allContributions.reduce((sum, c) => sum + Number(c.amount), 0);
      const average = total / allContributions.length;
      
      return {
        total_amount: total,
        contribution_count: allContributions.length,
        average_contribution: average
      };
    }
    
    return null;
  }, [goalId, goalContributionsData, allContributions]);

  // Análisis por cuenta
  const getContributionsByAccount = useCallback(() => {
    const accountGroups: Record<string, { total: number; count: number }> = {};
    
    contributions.forEach(contribution => {
      const accountName = contribution.from_account_name || 'Cuenta Desconocida';
      
      if (!accountGroups[accountName]) {
        accountGroups[accountName] = { total: 0, count: 0 };
      }
      
      accountGroups[accountName].total += Number(contribution.amount);
      accountGroups[accountName].count += 1;
    });
    
    return Object.entries(accountGroups).map(([account_name, data]) => ({
      account_name,
      total: data.total,
      count: data.count
    })).sort((a, b) => b.total - a.total);
  }, [contributions]);

  // Totales por mes
  const getTotalsByMonth = useCallback(() => {
    const monthGroups: Record<string, { total: number; count: number }> = {};
    
    contributions.forEach(contribution => {
      const date = new Date(contribution.date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      
      if (!monthGroups[monthKey]) {
        monthGroups[monthKey] = { total: 0, count: 0 };
      }
      
      monthGroups[monthKey].total += Number(contribution.amount);
      monthGroups[monthKey].count += 1;
    });
    
    return Object.entries(monthGroups)
      .map(([month, data]) => ({
        month,
        total: data.total,
        count: data.count
      }))
      .sort((a, b) => a.month.localeCompare(b.month));
  }, [contributions]);

  // Promedio de contribución
  const getAverageContribution = useCallback(() => {
    if (contributions.length === 0) return 0;
    
    const total = contributions.reduce((sum, c) => sum + Number(c.amount), 0);
    return total / contributions.length;
  }, [contributions]);

  // Contribución más grande
  const getLargestContribution = useCallback(() => {
    if (contributions.length === 0) return null;
    
    return contributions.reduce((largest, current) => 
      Number(current.amount) > Number(largest.amount) ? current : largest
    );
  }, [contributions]);

  // Contribuciones recientes
  const getRecentContributions = useCallback((limit: number = 5) => {
    return [...contributions]
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      .slice(0, limit);
  }, [contributions]);

  // =====================================================
  // ESTADOS COMPUTADOS
  // =====================================================
  
  const loading = useMemo(() => 
    (goalId ? goalContributionsLoading : allContributionsLoading),
    [goalId, goalContributionsLoading, allContributionsLoading]
  );

  const error = useMemo(() => 
    (goalId ? goalContributionsError : allContributionsError) as ApiError,
    [goalId, goalContributionsError, allContributionsError]
  );

  // =====================================================
  // RETURN DEL HOOK
  // =====================================================
  return {
    // Estados principales
    contributions,
    loading,
    error,
    
    // Estadísticas
    statistics,
    
    // Acciones CRUD
    createContribution: useCallback(
      (goalId: number, data: CreateContributionData) => 
        createMutation.mutateAsync({ goalId, data }),
      [createMutation]
    ),
    updateContribution: useCallback(
      (id: number, updates: UpdateContributionData) => 
        updateMutation.mutateAsync({ id, updates }),
      [updateMutation]
    ),
    deleteContribution: deleteMutation.mutateAsync,
    getContribution,
    
    // Filtros y búsqueda
    filters,
    setFilters,
    
    // Utilidades
    refetch,
    
    // Estados de mutaciones
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    
    // Análisis de contribuciones
    getMonthlyTrend,
    getContributionsByAccount,
    getTotalsByMonth,
    getAverageContribution,
    getLargestContribution,
    getRecentContributions,
  };
};

// =====================================================
// HOOKS ESPECIALIZADOS
// =====================================================

// Hook para contribuciones de una meta específica
export const useGoalContributions = (goalId: number) => {
  return useContributions({ 
    goalId,
    enabled: !!goalId 
  });
};

// Hook para todas las contribuciones del usuario
export const useAllContributions = () => {
  return useContributions({ 
    enabled: true 
  });
};

// Hook para contribuciones recientes (dashboard)
export const useRecentContributions = (limit: number = 10) => {
  const hook = useContributions({
    initialFilters: {
      ordering: '-date',
      limit
    }
  });

  return {
    ...hook,
    recentContributions: hook.contributions.slice(0, limit)
  };
};

export default useContributions;