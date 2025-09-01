// =====================================================
// API ENDPOINTS - URLs reales del backend Django
// Actualizado: Auth (Rama 1) + Accounts (Rama 2) + Transactions (Rama 3) + Analytics (Rama 4) + Goals (Rama 5)
// =====================================================

// Base API URL
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// =====================================================
// AUTH ENDPOINTS (RAMA 1 - COMPLETADO ✅)
// =====================================================
export const AUTH_ENDPOINTS = {
  // JWT Authentication (django-rest-framework-simplejwt)
  LOGIN: '/token/',                    // POST - Obtener tokens JWT
  REFRESH: '/token/refresh/',          // POST - Refrescar access token
  
  // Custom Auth Endpoints (core app)
  REGISTER: '/auth/register/',         // POST - Registro de usuario
  DEMO: '/auth/demo/',                 // POST - Crear usuario demo
  PROFILE: '/auth/profile/',           // GET - Obtener perfil del usuario
} as const;

// =====================================================
// SETUP/UTILITY ENDPOINTS
// =====================================================
export const SETUP_ENDPOINTS = {
  RUN_MIGRATIONS: '/setup/run-migrations/',      // POST - Ejecutar migraciones
  CREATE_SUPERUSER: '/setup/create-superuser/',  // POST - Crear superusuario
} as const;

// =====================================================
// ACCOUNTS ENDPOINTS (RAMA 2 - COMPLETADO ✅)
// Basado en AccountViewSet real del backend
// =====================================================
export const ACCOUNTS_ENDPOINTS = {
  // Accounts CRUD
  ACCOUNTS: '/accounts/',                                      // GET, POST - Lista y crear cuentas
  ACCOUNT_DETAIL: (id: number) => `/accounts/${id}/`,         // GET, PUT, PATCH, DELETE
  
  // Account specific actions (@action del ViewSet)
  ACCOUNT_SUMMARY: '/accounts/summary/',                       // GET - Resumen financiero global
  ACCOUNT_TRANSACTIONS: (id: number) => `/accounts/${id}/transactions/`,    // GET - Transacciones de cuenta
  ACCOUNT_BALANCE_HISTORY: (id: number) => `/accounts/${id}/balance_history/`, // GET - Historial balance (30 días)
  ACCOUNT_RECONCILE: (id: number) => `/accounts/${id}/reconcile/`,          // POST - Conciliar balance real
} as const;

// =====================================================
// TRANSACTIONS ENDPOINTS (RAMA 3 - COMPLETADO ✅)
// Basado en urls.py y views.py reales del backend
// =====================================================
export const TRANSACTIONS_ENDPOINTS = {
  // ✅ Transactions CRUD (TransactionViewSet)
  TRANSACTIONS: '/transactions/',                              // GET, POST - Lista y crear transacciones
  TRANSACTION_DETAIL: (id: number) => `/transactions/${id}/`, // GET, PUT, PATCH, DELETE
  
  // ✅ Transaction custom actions (@action del ViewSet)
  TRANSACTION_RECENT: '/transactions/recent/',                 // GET - Últimas 10 transacciones
  TRANSACTION_BY_TYPE: '/transactions/by_type/',               // GET - Transacciones agrupadas por tipo
  TRANSACTION_SEARCH: '/transactions/search/',                 // GET - Búsqueda avanzada (?q=netflix)
  TRANSACTION_DASHBOARD: '/transactions/dashboard/',           // GET - Dashboard con métricas del período
  
  // ✅ Categories CRUD (CategoryViewSet)
  CATEGORIES: '/categories/',                                  // GET, POST - Lista y crear categorías
  CATEGORY_DETAIL: (id: number) => `/categories/${id}/`,      // GET, PUT, PATCH, DELETE
  
  // ✅ Category custom actions (@action del ViewSet)
  CATEGORIES_BY_TYPE: '/categories/by_type/',                  // GET - Categorías por income/expense
  CATEGORIES_HIERARCHY: '/categories/hierarchy/',              // GET - Estructura jerárquica
  CATEGORY_TRANSACTIONS: (id: number) => `/categories/${id}/transactions/`, // GET - Transacciones de categoría
  CATEGORY_MONTHLY_TREND: (id: number) => `/categories/${id}/monthly_trend/`, // GET - Tendencia mensual (12 meses)
  CATEGORIES_CREATE_DEFAULTS: '/categories/create_defaults/',  // POST - Crear categorías predeterminadas
  CATEGORIES_STATISTICS: '/categories/statistics/',            // GET - Estadísticas generales
  CATEGORIES_SUMMARY_REPORT: '/categories/summary_report/',    // GET - Reporte de resumen con comparativas
  
  // ✅ Budget Alerts (BudgetAlertViewSet - ReadOnly)
  BUDGET_ALERTS: '/budget-alerts/',                           // GET - Todas las alertas del usuario
  BUDGET_ALERT_DETAIL: (id: number) => `/budget-alerts/${id}/`, // GET - Alerta específica
  BUDGET_ALERT_MARK_READ: (id: number) => `/budget-alerts/${id}/mark_read/`, // POST - Marcar como leída
  BUDGET_ALERTS_UNREAD: '/budget-alerts/unread/',             // GET - Solo alertas no leídas
} as const;

// =====================================================
// ANALYTICS ENDPOINTS (RAMA 4 - COMPLETADO ✅)
// Basado en ReportsViewSet real del backend
// =====================================================
export const ANALYTICS_ENDPOINTS = {
  // ✅ Reports ViewSet (@action methods)
  REPORTS_DASHBOARD: '/reports/dashboard/',                    // GET - Dashboard completo de analytics
  REPORTS_INCOME_VS_EXPENSES: '/reports/income_vs_expenses/', // GET - Ingresos vs gastos por período
  REPORTS_CATEGORY_DISTRIBUTION: '/reports/category_distribution/', // GET - Distribución por categorías
  REPORTS_BALANCE_TIMELINE: '/reports/balance_timeline/',     // GET - Timeline de balances
  REPORTS_TOP_CATEGORIES: '/reports/top_categories/',         // GET - Top categorías por gasto
  REPORTS_MONTHLY_SUMMARY: '/reports/monthly_summary/',       // GET - Resumen mensual
  REPORTS_YEARLY_COMPARISON: '/reports/yearly_comparison/',   // GET - Comparación año anterior
  REPORTS_CASH_FLOW: '/reports/cash_flow/',                   // GET - Flujo de efectivo
  REPORTS_ACCOUNT_PERFORMANCE: '/reports/account_performance/', // GET - Rendimiento por cuenta
  REPORTS_FINANCIAL_HEALTH: '/reports/financial_health/',     // GET - Indicadores de salud financiera
} as const;

// =====================================================
// GOALS ENDPOINTS (RAMA 5 - COMPLETADO ✅)
// Basado en urls.py y views.py reales del backend de goals
// =====================================================
export const GOALS_ENDPOINTS = {
  // ✅ Goals CRUD (FinancialGoalViewSet)
  GOALS: '/goals/',                                            // GET, POST - Lista y crear metas
  GOAL_DETAIL: (id: number) => `/goals/${id}/`,              // GET, PUT, PATCH, DELETE
  
  // ✅ Goal custom actions (@action del ViewSet)
  GOALS_DASHBOARD: '/goals/dashboard/',                        // GET - Dashboard completo de metas
  GOALS_SUMMARY: '/goals/summary/',                           // GET - Resumen rápido para widgets
  GOAL_ADD_CONTRIBUTION: (id: number) => `/goals/${id}/add_contribution/`, // POST - Agregar contribución
  GOAL_CONTRIBUTIONS: (id: number) => `/goals/${id}/contributions/`,       // GET - Ver contribuciones de meta
  GOAL_ADD_MILESTONE: (id: number) => `/goals/${id}/add_milestone/`,       // POST - Agregar hito
  GOAL_PAUSE: (id: number) => `/goals/${id}/pause/`,                       // POST - Pausar meta
  GOAL_RESUME: (id: number) => `/goals/${id}/resume/`,                     // POST - Reanudar meta
  GOAL_COMPLETE: (id: number) => `/goals/${id}/complete/`,                 // POST - Completar meta manualmente
  GOAL_ANALYTICS: (id: number) => `/goals/${id}/analytics/`,               // GET - Análisis detallado de meta
  
  // ✅ Goal Contributions CRUD (GoalContributionViewSet)
  CONTRIBUTIONS: '/goal-contributions/',                       // GET, POST - Lista y crear contribuciones
  CONTRIBUTION_DETAIL: (id: number) => `/goal-contributions/${id}/`, // GET, PUT, PATCH, DELETE
  
  // ✅ Goal Templates (GoalTemplateViewSet - ReadOnly)
  TEMPLATES: '/goal-templates/',                               // GET - Lista plantillas
  TEMPLATE_DETAIL: (id: number) => `/goal-templates/${id}/`,  // GET - Plantilla específica
  TEMPLATE_CREATE_GOAL: (id: number) => `/goal-templates/${id}/create_goal/`, // POST - Crear meta desde plantilla
  TEMPLATES_BY_CATEGORY: '/goal-templates/by_category/',       // GET - Plantillas agrupadas por tipo
  
  // ✅ Utility endpoints (@api_view functions)
  SETUP_TEMPLATES: '/setup/create-goal-templates/',           // POST - Crear plantillas predeterminadas
  GOALS_CALENDAR: '/goals-calendar/',                         // GET - Vista calendario (?year=2024&month=12)
  GOALS_INSIGHTS: '/goals-insights/',                         // GET - Insights inteligentes sobre metas
} as const;

// =====================================================
// UNIFIED ENDPOINTS OBJECT
// =====================================================
export const ENDPOINTS = {
  // Auth
  ...AUTH_ENDPOINTS,
  
  // Setup
  ...SETUP_ENDPOINTS,
  
  // Business Logic
  ACCOUNTS: ACCOUNTS_ENDPOINTS,
  TRANSACTIONS: TRANSACTIONS_ENDPOINTS,
  ANALYTICS: ANALYTICS_ENDPOINTS,
  GOALS: GOALS_ENDPOINTS,
} as const;

// =====================================================
// ENDPOINT BUILDERS
// =====================================================

/**
 * Construir URL completa del endpoint
 */
export const buildEndpointUrl = (endpoint: string): string => {
  return `${API_BASE_URL}${endpoint}`;
};

/**
 * Construir URL con parámetros de query
 */
export const buildUrlWithParams = (
  endpoint: string, 
  params: Record<string, any>
): string => {
  const url = new URL(buildEndpointUrl(endpoint));
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      // Manejar arrays para filtros múltiples (ej: tags=comida,trabajo)
      if (Array.isArray(value)) {
        url.searchParams.append(key, value.join(','));
      } else {
        url.searchParams.append(key, String(value));
      }
    }
  });
  
  return url.toString();
};

/**
 * Validar si un endpoint existe
 */
export const isValidEndpoint = (endpoint: string): boolean => {
  const allEndpoints = [
    ...Object.values(AUTH_ENDPOINTS),
    ...Object.values(SETUP_ENDPOINTS),
    ...Object.values(ACCOUNTS_ENDPOINTS).filter(ep => typeof ep === 'string'),
    ...Object.values(TRANSACTIONS_ENDPOINTS).filter(ep => typeof ep === 'string'),
    ...Object.values(ANALYTICS_ENDPOINTS),
    ...Object.values(GOALS_ENDPOINTS).filter(ep => typeof ep === 'string'),
  ];
  
  return allEndpoints.includes(endpoint as typeof allEndpoints[number]);
};

// =====================================================
// ENDPOINT GROUPS FOR PERMISSIONS
// =====================================================

export const ENDPOINT_GROUPS = {
  PUBLIC: [
    AUTH_ENDPOINTS.LOGIN,
    AUTH_ENDPOINTS.REFRESH,
    AUTH_ENDPOINTS.REGISTER,
    AUTH_ENDPOINTS.DEMO,
  ],
  
  AUTHENTICATED: [
    AUTH_ENDPOINTS.PROFILE,
    ACCOUNTS_ENDPOINTS.ACCOUNTS,
    ACCOUNTS_ENDPOINTS.ACCOUNT_SUMMARY,
    TRANSACTIONS_ENDPOINTS.TRANSACTIONS,
    TRANSACTIONS_ENDPOINTS.CATEGORIES,
    TRANSACTIONS_ENDPOINTS.BUDGET_ALERTS,
    ANALYTICS_ENDPOINTS.REPORTS_DASHBOARD,
    GOALS_ENDPOINTS.GOALS,
    GOALS_ENDPOINTS.CONTRIBUTIONS,
    GOALS_ENDPOINTS.TEMPLATES,
  ],
  
  ADMIN_ONLY: [
    SETUP_ENDPOINTS.RUN_MIGRATIONS,
    SETUP_ENDPOINTS.CREATE_SUPERUSER,
  ],
} as const;

// =====================================================
// TRANSACTIONS SPECIFIC HELPERS (RAMA 3 - COMPLETADO ✅)
// =====================================================

/**
 * Construir filtros de transactions para query params
 */
export const buildTransactionFilters = (filters: Record<string, any>): Record<string, any> => {
  const cleanFilters: Record<string, any> = {};
  
  // Mapear filtros específicos de transactions según TransactionFilter
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      switch (key) {
        // Montos
        case 'minAmount':
          cleanFilters.min_amount = value;
          break;
        case 'maxAmount':
          cleanFilters.max_amount = value;
          break;
        
        // Cuentas
        case 'fromAccount':
          cleanFilters.from_account = value;
          break;
        case 'toAccount':
          cleanFilters.to_account = value;
          break;
        case 'account':
          cleanFilters.account = value;
          break;
        case 'bankName':
          cleanFilters.bank = value;
          break;
        case 'accountType':
          cleanFilters.account_type = value;
          break;
        
        // Fechas
        case 'dateAfter':
          cleanFilters.date_after = value;
          break;
        case 'dateBefore':
          cleanFilters.date_before = value;
          break;
        
        // Búsqueda
        case 'search':
          cleanFilters.description = value;
          break;
        
        // Referencias y ubicación
        case 'hasReference':
          cleanFilters.has_reference = value;
          break;
        
        // Recurrencia
        case 'isRecurring':
          cleanFilters.is_recurring = value;
          break;
        case 'recurringFrequency':
          cleanFilters.recurring_frequency = value;
          break;
        
        // Flujo de efectivo
        case 'cashFlow':
          cleanFilters.cash_flow = value;
          break;
        
        // Etiquetas (convertir array a string separado por comas)
        case 'tags':
          if (Array.isArray(value)) {
            cleanFilters.tags = value.join(',');
          } else {
            cleanFilters.tags = value;
          }
          break;
        
        // Campos directos
        default:
          cleanFilters[key] = value;
      }
    }
  });
  
  return cleanFilters;
};

/**
 * Construir filtros de categories para query params
 */
export const buildCategoryFilters = (filters: Record<string, any>): Record<string, any> => {
  const cleanFilters: Record<string, any> = {};
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      switch (key) {
        case 'categoryType':
          cleanFilters.category_type = value;
          break;
        case 'isActive':
          cleanFilters.is_active = value;
          break;
        case 'parentId':
          cleanFilters.parent = value;
          break;
        default:
          cleanFilters[key] = value;
      }
    }
  });
  
  return cleanFilters;
};

// =====================================================
// ACCOUNTS SPECIFIC HELPERS (RAMA 2 - COMPLETADO ✅)
// =====================================================

/**
 * Construir filtros de accounts para query params
 */
export const buildAccountFilters = (filters: Record<string, any>): Record<string, any> => {
  const cleanFilters: Record<string, any> = {};
  
  // Mapear filtros específicos de accounts
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      switch (key) {
        case 'accountType':
          cleanFilters.account_type = value;
          break;
        case 'minBalance':
          cleanFilters.min_balance = value;
          break;
        case 'maxBalance':
          cleanFilters.max_balance = value;
          break;
        case 'bankName':
          cleanFilters.bank_name = value;
          break;
        case 'hasTransactions':
          cleanFilters.has_transactions = value;
          break;
        case 'includeInReports':
          cleanFilters.include_in_reports = value;
          break;
        case 'isActive':
          cleanFilters.is_active = value;
          break;
        default:
          cleanFilters[key] = value;
      }
    }
  });
  
  return cleanFilters;
};

// =====================================================
// GOALS SPECIFIC HELPERS (RAMA 5 - NUEVO ✅)
// =====================================================

/**
 * Construir filtros de goals para query params
 */
export const buildGoalFilters = (filters: Record<string, any>): Record<string, any> => {
  const cleanFilters: Record<string, any> = {};
  
  // Mapear filtros específicos de goals según FinancialGoalFilter
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      switch (key) {
        // Montos
        case 'minTargetAmount':
          cleanFilters.min_target_amount = value;
          break;
        case 'maxTargetAmount':
          cleanFilters.max_target_amount = value;
          break;
        case 'minCurrentAmount':
          cleanFilters.min_current_amount = value;
          break;
        case 'maxCurrentAmount':
          cleanFilters.max_current_amount = value;
          break;
        
        // Fechas
        case 'startDateAfter':
          cleanFilters.start_date_after = value;
          break;
        case 'startDateBefore':
          cleanFilters.start_date_before = value;
          break;
        case 'targetDateAfter':
          cleanFilters.target_date_after = value;
          break;
        case 'targetDateBefore':
          cleanFilters.target_date_before = value;
          break;
        
        // Cuenta asociada
        case 'associatedAccount':
          cleanFilters.associated_account = value;
          break;
        case 'bankName':
          cleanFilters.bank = value;
          break;
        
        // Progreso
        case 'minProgress':
          cleanFilters.min_progress = value;
          break;
        case 'maxProgress':
          cleanFilters.max_progress = value;
          break;
        
        // Tiempo restante
        case 'daysRemainingLess':
          cleanFilters.days_remaining_less_than = value;
          break;
        case 'daysRemainingMore':
          cleanFilters.days_remaining_more_than = value;
          break;
        
        // Booleanos
        case 'isOverdue':
          cleanFilters.is_overdue = value;
          break;
        case 'hasContributions':
          cleanFilters.has_contributions = value;
          break;
        case 'isOnTrack':
          cleanFilters.is_on_track = value;
          break;
        case 'enableReminders':
          cleanFilters.enable_reminders = value;
          break;
        
        // Categorías relacionadas
        case 'relatedCategory':
          cleanFilters.related_category = value;
          break;
        
        // Campos directos
        default:
          cleanFilters[key] = value;
      }
    }
  });
  
  return cleanFilters;
};

/**
 * Construir filtros de contributions para query params
 */
export const buildContributionFilters = (filters: Record<string, any>): Record<string, any> => {
  const cleanFilters: Record<string, any> = {};
  
  // Mapear filtros específicos de contributions según GoalContributionFilter
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      switch (key) {
        // Relaciones
        case 'goalId':
          cleanFilters.goal = value;
          break;
        case 'goalTitle':
          cleanFilters.goal_title = value;
          break;
        case 'fromAccount':
          cleanFilters.from_account = value;
          break;
        case 'bankName':
          cleanFilters.bank = value;
          break;
        
        // Montos
        case 'minAmount':
          cleanFilters.min_amount = value;
          break;
        case 'maxAmount':
          cleanFilters.max_amount = value;
          break;
        
        // Fechas
        case 'dateAfter':
          cleanFilters.date_after = value;
          break;
        case 'dateBefore':
          cleanFilters.date_before = value;
          break;
        
        // Tipo de contribución
        case 'contributionType':
          cleanFilters.contribution_type = value;
          break;
        
        // Booleanos
        case 'isRecurring':
          cleanFilters.is_recurring = value;
          break;
        case 'hasTransaction':
          cleanFilters.has_transaction = value;
          break;
        
        // Campos directos
        default:
          cleanFilters[key] = value;
      }
    }
  });
  
  return cleanFilters;
};

// =====================================================
// HELPER FUNCTIONS
// =====================================================

/**
 * Verificar si un endpoint requiere autenticación
 */
export const requiresAuth = (endpoint: string): boolean => {
  return !ENDPOINT_GROUPS.PUBLIC.includes(endpoint as any);
};

/**
 * Verificar si un endpoint es solo para admin
 */
export const isAdminOnly = (endpoint: string): boolean => {
  return ENDPOINT_GROUPS.ADMIN_ONLY.includes(endpoint as any);
};

/**
 * Obtener el método HTTP típico para un endpoint
 */
export const getEndpointMethod = (endpoint: string): string => {
  if (endpoint.includes('/detail/') || endpoint.includes('/{id}/')) {
    return 'GET'; // Detail endpoints por defecto GET
  }
  
  if (endpoint.endsWith('/')) {
    return 'GET'; // List endpoints por defecto GET
  }
  
  return 'GET'; // Default
};

export default ENDPOINTS;