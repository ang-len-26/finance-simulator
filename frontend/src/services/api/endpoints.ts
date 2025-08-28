// =====================================================
// API ENDPOINTS - URLs reales del backend Django
// Actualizado: Auth (Rama 1) + Accounts (Rama 2)
// =====================================================

// Base API URL
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// =====================================================
// AUTH ENDPOINTS (RAMA 1 - COMPLETADO)
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
// ACCOUNTS ENDPOINTS (RAMA 2 - COMPLETADO)
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
// TRANSACTIONS ENDPOINTS (PENDIENTE RAMA 3)
// =====================================================
export const TRANSACTIONS_ENDPOINTS = {
  // Transactions CRUD
  TRANSACTIONS: '/transactions/',                // GET, POST - Lista y crear transacciones
  TRANSACTION_DETAIL: (id: number) => `/transactions/${id}/`,  // GET, PUT, PATCH, DELETE
  
  // Categories CRUD
  CATEGORIES: '/categories/',                    // GET, POST - Lista y crear categorías
  CATEGORY_DETAIL: (id: number) => `/categories/${id}/`,      // GET, PUT, PATCH, DELETE
  
  // Transaction specific actions (POR CONFIRMAR EN RAMA 3)
  TRANSACTION_SUMMARY: '/transactions/summary/', // GET - Resumen de transacciones
  BULK_IMPORT: '/transactions/bulk-import/',     // POST - Importar transacciones masivas
} as const;

// =====================================================
// ANALYTICS ENDPOINTS (PENDIENTE RAMA 4)
// =====================================================
export const ANALYTICS_ENDPOINTS = {
  // Reports and Analytics (POR CONFIRMAR)
  REPORTS: '/reports/',                          // GET - Reportes generales
  METRICS: '/metrics/',                          // GET - Métricas financieras
  ALERTS: '/alerts/',                            // GET - Alertas de presupuesto
  
  // Specific analytics (POR CONFIRMAR)
  INCOME_VS_EXPENSES: '/reports/income-vs-expenses/',
  CATEGORY_DISTRIBUTION: '/reports/category-distribution/',
  BALANCE_TIMELINE: '/reports/balance-timeline/',
  FINANCIAL_RATIOS: '/reports/financial-ratios/',
} as const;

// =====================================================
// GOALS ENDPOINTS (PENDIENTE RAMA 5)
// =====================================================
export const GOALS_ENDPOINTS = {
  // Goals CRUD (POR CONFIRMAR)
  GOALS: '/goals/',                              // GET, POST - Lista y crear metas
  GOAL_DETAIL: (id: number) => `/goals/${id}/`, // GET, PUT, PATCH, DELETE
  
  // Goal Contributions (POR CONFIRMAR)
  CONTRIBUTIONS: '/goal-contributions/',         // GET, POST - Contribuciones
  CONTRIBUTION_DETAIL: (id: number) => `/goal-contributions/${id}/`,
  
  // Goal Templates (POR CONFIRMAR)
  TEMPLATES: '/goal-templates/',                 // GET - Plantillas de metas
  TEMPLATE_DETAIL: (id: number) => `/goal-templates/${id}/`,
  
  // Goal specific actions (POR CONFIRMAR)
  GOAL_PROGRESS: '/goals/progress/',             // GET - Progreso de metas
  GOAL_INSIGHTS: '/goals/insights/',             // GET - Insights de metas
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
      // Manejar arrays para filtros múltiples (ej: account_type=checking,savings)
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
    ANALYTICS_ENDPOINTS.REPORTS,
    GOALS_ENDPOINTS.GOALS,
  ],
  
  ADMIN_ONLY: [
    SETUP_ENDPOINTS.RUN_MIGRATIONS,
    SETUP_ENDPOINTS.CREATE_SUPERUSER,
  ],
} as const;

// =====================================================
// ACCOUNTS SPECIFIC HELPERS (RAMA 2)
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