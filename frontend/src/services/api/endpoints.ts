// =====================================================
// API ENDPOINTS - URLs reales del backend Django
// Actualizado: Auth (Rama 1) + Accounts (Rama 2) + Transactions (Rama 3) + Analytics (Rama 4)
// =====================================================

// Base API URL
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// =====================================================
// AUTH ENDPOINTS (RAMA 1 - COMPLETADO)
// Basado en auth/urls.py y views.py reales del backend
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
// Basado en accounts/urls.py y views.py reales del backend
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
// TRANSACTIONS ENDPOINTS (RAMA 3 - COMPLETADO)
// Basado en transactions/urls.py y views.py reales del backend
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
// ANALYTICS ENDPOINTS (RAMA 4 - COMPLETADO)
// Basado en analytics/urls.py y views.py reales del backend
// =====================================================
export const ANALYTICS_ENDPOINTS = {
  // ✅ Reports CRUD (ReportsViewSet)
  REPORTS: '/reports/',                                        // GET, POST - Métricas financieras CRUD
  REPORT_DETAIL: (id: number) => `/reports/${id}/`,           // GET, PUT, PATCH, DELETE - Métrica específica
  
  // ✅ Dashboard y métricas principales (@action methods)
  REPORTS_METRICS: '/reports/metrics/',                        // GET - Métricas principales + comparativas (4 tarjetas superiores)
  REPORTS_INCOME_VS_EXPENSES: '/reports/income-vs-expenses/',  // GET - Gráfico ingresos vs gastos mensuales (12 meses)
  REPORTS_BALANCE_TIMELINE: '/reports/balance-timeline/',      // GET - Timeline balance acumulado día por día
  REPORTS_CATEGORY_DISTRIBUTION: '/reports/category-distribution/', // GET - Distribución gastos por categoría (pie/dona)
  REPORTS_TOP_CATEGORIES: '/reports/top-categories/',          // GET - Top 5 categorías con detalles y tendencias
  REPORTS_RECENT_TRANSACTIONS: '/reports/recent-transactions/', // GET - Transacciones recientes con íconos
  REPORTS_FINANCIAL_METRICS: '/reports/financial-metrics/',   // GET - Métricas precalculadas por período
  
  // ✅ Sistema de alertas (@action methods)
  REPORTS_ALERTS: '/reports/alerts/',                          // GET - Alertas de presupuesto con filtros
  REPORTS_MARK_ALERT_READ: '/reports/mark-alert-read/',        // POST - Marcar alertas como leídas (bulk)
  
  // ✅ Análisis avanzado (@action methods)
  REPORTS_CATEGORY_TRENDS: '/reports/category-trends/',        // GET - Tendencias de categorías en tiempo (6-8 períodos)
  
  // ✅ Endpoints independientes (function-based views)
  REPORTS_OVERVIEW: '/reports-overview/',                      // GET - Dashboard completo en una sola llamada
  FINANCIAL_RATIOS: '/financial-ratios/',                      // GET - Ratios financieros profesionales + recomendaciones
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
    ...Object.values(ANALYTICS_ENDPOINTS).filter(ep => typeof ep === 'string'),
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
    ANALYTICS_ENDPOINTS.REPORTS,
    ANALYTICS_ENDPOINTS.REPORTS_OVERVIEW,
    ANALYTICS_ENDPOINTS.FINANCIAL_RATIOS,
    GOALS_ENDPOINTS.GOALS,
  ],
  
  ADMIN_ONLY: [
    SETUP_ENDPOINTS.RUN_MIGRATIONS,
    SETUP_ENDPOINTS.CREATE_SUPERUSER,
  ],
} as const;

// =====================================================
// ANALYTICS SPECIFIC HELPERS (RAMA 4)
// =====================================================

/**
 * Construir filtros de analytics para query params
 */
export const buildAnalyticsFilters = (filters: Record<string, any>): Record<string, any> => {
  const cleanFilters: Record<string, any> = {};
  
  // Mapear filtros específicos de analytics
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      switch (key) {
        // Períodos
        case 'periodType':
          cleanFilters.period_type = value;
          break;
        case 'period':
          cleanFilters.period = value; // monthly, quarterly, yearly, custom, last_30_days, last_90_days
          break;
        case 'startDate':
          cleanFilters.start_date = value;
          break;
        case 'endDate':
          cleanFilters.end_date = value;
          break;
        
        // Alertas
        case 'severity':
          cleanFilters.severity = value; // low, medium, high, critical
          break;
        case 'alertType':
          cleanFilters.alert_type = value; // budget_exceeded, unusual_expense, income_drop, account_low, category_spike
          break;
        case 'isRead':
          cleanFilters.is_read = value;
          break;
        case 'includeDismissed':
          cleanFilters.include_dismissed = value;
          break;
        
        // Filtros de datos
        case 'limit':
          cleanFilters.limit = value;
          break;
        case 'categoryId':
          cleanFilters.category = value;
          break;
        case 'accountId':
          cleanFilters.account = value;
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
 * Construir parámetros para reportes con períodos predefinidos
 */
export const buildReportPeriodParams = (period: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly' | 'last_30_days' | 'last_90_days' | 'custom', customDates?: { start: string; end: string }): Record<string, any> => {
  const params: Record<string, any> = { period };
  
  if (period === 'custom' && customDates) {
    params.start_date = customDates.start;
    params.end_date = customDates.end;
  }
  
  return params;
};

/**
 * Construir parámetros para alertas con filtros comunes
 */
export const buildAlertParams = (filters: {
  severity?: 'low' | 'medium' | 'high' | 'critical';
  alertType?: 'budget_exceeded' | 'unusual_expense' | 'income_drop' | 'account_low' | 'category_spike';
  unreadOnly?: boolean;
  includeDismissed?: boolean;
  limit?: number;
}): Record<string, any> => {
  const params: Record<string, any> = {};
  
  if (filters.severity) params.severity = filters.severity;
  if (filters.alertType) params.alert_type = filters.alertType;
  if (filters.unreadOnly) params.is_read = 'false';
  if (filters.includeDismissed !== undefined) params.include_dismissed = filters.includeDismissed;
  if (filters.limit) params.limit = filters.limit;
  
  return params;
};

// =====================================================
// TRANSACTIONS SPECIFIC HELPERS (RAMA 3)
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
// AUTH SPECIFIC HELPERS (RAMA 1)
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