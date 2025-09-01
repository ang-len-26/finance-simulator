import { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { goalsApi } from '../services/goalsApi';
import { 
  GoalTemplate, 
  CreateGoalFromTemplateData,
  FinancialGoal,
  GoalType
} from '../types/goals.types';
import { ApiError } from '@/types/api.types';

// =====================================================
// TIPOS PARA EL HOOK
// =====================================================
export interface UseGoalTemplatesOptions {
  enabled?: boolean;
  refetchInterval?: number;
}

export interface TemplatesByCategory {
  [category: string]: GoalTemplate[];
}

export interface UseGoalTemplatesReturn {
  // Estados principales
  templates: GoalTemplate[];
  templatesByCategory: TemplatesByCategory;
  loading: boolean;
  error: ApiError | null;
  
  // Acciones
  createGoalFromTemplate: (templateId: number, customData?: Partial<CreateGoalFromTemplateData>) => Promise<FinancialGoal>;
  getTemplate: (id: number) => GoalTemplate | undefined;
  getTemplatesByType: (goalType: GoalType) => GoalTemplate[];
  
  // Utilidades
  refetch: () => Promise<void>;
  
  // Funciones de análisis
  getPopularTemplates: () => GoalTemplate[];
  getRecommendedTemplates: () => GoalTemplate[];
  calculateSuggestedAmount: (template: GoalTemplate) => number;
  
  // Estados de mutaciones
  isCreatingFromTemplate: boolean;
  
  // Funciones de filtrado
  searchTemplates: (query: string) => GoalTemplate[];
  filterByCategory: (category: GoalType) => GoalTemplate[];
}

// =====================================================
// CATEGORÍAS DE PLANTILLAS
// =====================================================
export const TEMPLATE_CATEGORIES: Record<GoalType, { label: string; icon: string; description: string }> = {
  savings: {
    label: 'Ahorro',
    icon: 'piggy-bank',
    description: 'Metas para ahorrar dinero'
  },
  expense_reduction: {
    label: 'Reducir Gastos',
    icon: 'trending-down',
    description: 'Metas para reducir gastos específicos'
  },
  income_increase: {
    label: 'Aumentar Ingresos',
    icon: 'trending-up',
    description: 'Metas para incrementar ingresos'
  },
  debt_payment: {
    label: 'Pagar Deudas',
    icon: 'credit-card',
    description: 'Metas para eliminar deudas'
  },
  emergency_fund: {
    label: 'Fondo de Emergencia',
    icon: 'shield',
    description: 'Crear un fondo para emergencias'
  },
  investment: {
    label: 'Inversión',
    icon: 'trending-up',
    description: 'Metas de inversión y crecimiento'
  },
  purchase: {
    label: 'Compras',
    icon: 'shopping-cart',
    description: 'Ahorrar para compras específicas'
  },
  vacation: {
    label: 'Vacaciones',
    icon: 'plane',
    description: 'Ahorrar para viajes y vacaciones'
  },
  education: {
    label: 'Educación',
    icon: 'graduation-cap',
    description: 'Inversión en educación y cursos'
  },
  retirement: {
    label: 'Jubilación',
    icon: 'clock',
    description: 'Preparación para la jubilación'
  },
  other: {
    label: 'Otros',
    icon: 'more-horizontal',
    description: 'Otras metas financieras'
  }
};

// =====================================================
// HOOK PRINCIPAL - useGoalTemplates
// =====================================================
export const useGoalTemplates = (options: UseGoalTemplatesOptions = {}): UseGoalTemplatesReturn => {
  const queryClient = useQueryClient();
  const { enabled = true, refetchInterval } = options;
  
  // Estados locales
  const [searchQuery, setSearchQuery] = useState('');

  // =====================================================
  // QUERIES - CONSULTAS PRINCIPALES
  // =====================================================
  
  // Query principal - Todas las plantillas
  const {
    data: templates = [],
    isLoading: templatesLoading,
    error: templatesError,
    refetch: refetchTemplates
  } = useQuery({
    queryKey: ['goal-templates', 'list'],
    queryFn: goalsApi.getGoalTemplates,
    enabled,
    refetchInterval,
    staleTime: 30 * 60 * 1000, // 30 minutos (las plantillas no cambian frecuentemente)
  });

  // Query - Plantillas por categoría
  const {
    data: templatesByCategory = {},
    isLoading: templatesByCategoryLoading,
    error: templatesByCategoryError
  } = useQuery({
    queryKey: ['goal-templates', 'by-category'],
    queryFn: goalsApi.getTemplatesByCategory,
    enabled,
    staleTime: 30 * 60 * 1000,
  });

  // =====================================================
  // MUTATIONS - OPERACIONES
  // =====================================================
  
  // Crear meta desde plantilla
  const createFromTemplateMutation = useMutation({
    mutationFn: ({ templateId, customData }: { templateId: number; customData?: Partial<CreateGoalFromTemplateData> }) =>
      goalsApi.createGoalFromTemplate(templateId, customData || {}),
    onSuccess: (newGoal) => {
      // Invalidar cache de metas para reflejar la nueva meta creada
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      
      // Opcional: agregar la nueva meta al cache local si es necesario
      queryClient.setQueryData(
        ['goals', 'list'],
        (oldGoals: any[] = []) => [newGoal, ...oldGoals]
      );
    },
  });

  // =====================================================
  // FUNCIONES PÚBLICAS
  // =====================================================
  
  // Obtener plantilla específica
  const getTemplate = useCallback((id: number): GoalTemplate | undefined => {
    return templates.find(template => template.id === id);
  }, [templates]);

  // Obtener plantillas por tipo
  const getTemplatesByType = useCallback((goalType: GoalType): GoalTemplate[] => {
    return templates.filter(template => template.goal_type === goalType);
  }, [templates]);

  // Refetch general
  const refetch = useCallback(async () => {
    await Promise.all([
      refetchTemplates(),
      queryClient.invalidateQueries({ queryKey: ['goal-templates', 'by-category'] })
    ]);
  }, [refetchTemplates, queryClient]);

  // =====================================================
  // FUNCIONES DE ANÁLISIS Y RECOMENDACIONES
  // =====================================================
  
  // Plantillas más populares (basado en sort_order)
  const getPopularTemplates = useCallback((): GoalTemplate[] => {
    return [...templates]
      .sort((a, b) => a.sort_order - b.sort_order)
      .slice(0, 6); // Top 6
  }, [templates]);

  // Plantillas recomendadas (lógica personalizable)
  const getRecommendedTemplates = useCallback((): GoalTemplate[] => {
    // Por ahora, priorizar fondo de emergencia y ahorro básico
    const priorityTypes: GoalType[] = ['emergency_fund', 'savings', 'debt_payment'];
    
    const recommended = templates.filter(template => 
      priorityTypes.includes(template.goal_type)
    ).slice(0, 4);

    // Si no hay suficientes, agregar otras populares
    if (recommended.length < 4) {
      const remaining = getPopularTemplates()
        .filter(template => !recommended.some(rec => rec.id === template.id))
        .slice(0, 4 - recommended.length);
      
      recommended.push(...remaining);
    }

    return recommended;
  }, [templates, getPopularTemplates]);

  // Calcular monto sugerido personalizado
  const calculateSuggestedAmount = useCallback((template: GoalTemplate): number => {
    // Esta función podría usar datos del usuario para personalizar el monto
    // Por ahora, usar el monto calculado de la plantilla
    return template.suggested_amount_calculated || template.suggested_amount || 1000;
  }, []);

  // =====================================================
  // FUNCIONES DE FILTRADO Y BÚSQUEDA
  // =====================================================
  
  // Buscar plantillas por texto
  const searchTemplates = useCallback((query: string): GoalTemplate[] => {
    if (!query.trim()) return templates;
    
    const searchTerm = query.toLowerCase().trim();
    
    return templates.filter(template => 
      template.name.toLowerCase().includes(searchTerm) ||
      template.description.toLowerCase().includes(searchTerm) ||
      TEMPLATE_CATEGORIES[template.goal_type]?.label.toLowerCase().includes(searchTerm)
    );
  }, [templates]);

  // Filtrar por categoría
  const filterByCategory = useCallback((category: GoalType): GoalTemplate[] => {
    return templates.filter(template => template.goal_type === category);
  }, [templates]);

  // =====================================================
  // ESTADOS COMPUTADOS
  // =====================================================
  
  const loading = useMemo(() => 
    templatesLoading || templatesByCategoryLoading,
    [templatesLoading, templatesByCategoryLoading]
  );

  const error = useMemo(() => 
    templatesError || templatesByCategoryError,
    [templatesError, templatesByCategoryError]
  ) as ApiError;

  // Procesar plantillas por categoría con información adicional
  const processedTemplatesByCategory = useMemo(() => {
    if (Object.keys(templatesByCategory).length > 0) {
      return templatesByCategory;
    }

    // Si no hay datos de la API, agrupar manualmente
    const grouped: TemplatesByCategory = {};
    
    templates.forEach(template => {
      const category = template.goal_type;
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(template);
    });

    return grouped;
  }, [templatesByCategory, templates]);

  // =====================================================
  // FUNCIONES WRAPPER PARA CREAR METAS
  // =====================================================
  
  const createGoalFromTemplate = useCallback(
    async (templateId: number, customData?: Partial<CreateGoalFromTemplateData>): Promise<FinancialGoal> => {
      const template = getTemplate(templateId);
      
      if (!template) {
        throw new Error('Plantilla no encontrada');
      }

      // Preparar datos con valores por defecto de la plantilla
      const goalData: Partial<CreateGoalFromTemplateData> = {
        template_id: templateId,
        title: customData?.title || template.name,
        target_amount: customData?.target_amount || calculateSuggestedAmount(template),
        ...customData
      };

      return createFromTemplateMutation.mutateAsync({ 
        templateId, 
        customData: goalData 
      });
    },
    [getTemplate, calculateSuggestedAmount, createFromTemplateMutation]
  );

  // =====================================================
  // RETURN DEL HOOK
  // =====================================================
  return {
    // Estados principales
    templates,
    templatesByCategory: processedTemplatesByCategory,
    loading,
    error,
    
    // Acciones
    createGoalFromTemplate,
    getTemplate,
    getTemplatesByType,
    
    // Utilidades
    refetch,
    
    // Funciones de análisis
    getPopularTemplates,
    getRecommendedTemplates,
    calculateSuggestedAmount,
    
    // Estados de mutaciones
    isCreatingFromTemplate: createFromTemplateMutation.isPending,
    
    // Funciones de filtrado
    searchTemplates,
    filterByCategory,
  };
};

// =====================================================
// HOOKS ESPECIALIZADOS
// =====================================================

// Hook para plantillas populares/recomendadas (dashboard)
export const usePopularTemplates = () => {
  const { 
    templates, 
    loading, 
    error, 
    getPopularTemplates, 
    getRecommendedTemplates,
    createGoalFromTemplate,
    isCreatingFromTemplate
  } = useGoalTemplates();

  return {
    popularTemplates: getPopularTemplates(),
    recommendedTemplates: getRecommendedTemplates(),
    loading,
    error,
    createGoalFromTemplate,
    isCreating: isCreatingFromTemplate
  };
};

// Hook para explorar plantillas por categoría
export const useTemplatesByCategory = (category?: GoalType) => {
  const { 
    templatesByCategory, 
    loading, 
    error, 
    filterByCategory,
    createGoalFromTemplate 
  } = useGoalTemplates();

  const categoryTemplates = useMemo(() => {
    if (category) {
      return filterByCategory(category);
    }
    return templatesByCategory;
  }, [category, filterByCategory, templatesByCategory]);

  const categoryInfo = useMemo(() => {
    if (category) {
      return TEMPLATE_CATEGORIES[category];
    }
    return null;
  }, [category]);

  return {
    templates: categoryTemplates,
    categoryInfo,
    allCategories: Object.entries(TEMPLATE_CATEGORIES).map(([key, info]) => ({
      type: key as GoalType,
      ...info,
      count: templatesByCategory[key]?.length || 0
    })),
    loading,
    error,
    createGoalFromTemplate
  };
};

// Hook para búsqueda de plantillas
export const useTemplateSearch = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<GoalType | null>(null);
  
  const { 
    templates, 
    loading, 
    error, 
    searchTemplates, 
    filterByCategory,
    createGoalFromTemplate 
  } = useGoalTemplates();

  const filteredTemplates = useMemo(() => {
    let result = templates;

    // Aplicar filtro de categoría si está seleccionado
    if (selectedCategory) {
      result = filterByCategory(selectedCategory);
    }

    // Aplicar búsqueda por texto
    if (searchQuery.trim()) {
      result = result.filter(template => 
        template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return result;
  }, [templates, searchQuery, selectedCategory, filterByCategory]);

  return {
    // Estados
    searchQuery,
    selectedCategory,
    filteredTemplates,
    loading,
    error,
    
    // Acciones
    setSearchQuery,
    setSelectedCategory,
    clearSearch: () => {
      setSearchQuery('');
      setSelectedCategory(null);
    },
    createGoalFromTemplate,
    
    // Información de categorías
    categories: Object.entries(TEMPLATE_CATEGORIES).map(([key, info]) => ({
      type: key as GoalType,
      ...info
    })),
    
    // Estadísticas de búsqueda
    totalResults: filteredTemplates.length,
    hasResults: filteredTemplates.length > 0,
    isSearching: searchQuery.trim().length > 0 || selectedCategory !== null
  };
};

export default useGoalTemplates;