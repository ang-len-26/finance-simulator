export const API_ENDPOINTS = {
  // Authentication (compatible con DRF SimpleJWT)
  AUTH: {
    LOGIN: '/token/',
    REFRESH: '/token/refresh/',
    REGISTER: '/core/register/',
    PROFILE: '/core/profile/',
    DEMO: '/core/demo/',
  },

  // Core (usuarios y perfiles)
  CORE: {
    BASE: '/core/',
    USERS: '/core/users/',
    PROFILE: '/core/profile/',
    MIGRATE: '/core/migrate/',
    DEMO: '/core/demo/',
    SUPERUSER: '/core/superuser/',
  },

  // Accounts (cuentas bancarias)
  ACCOUNTS: {
    BASE: '/accounts/',
    DETAIL: (id: number) => `/accounts/${id}/`,
    TRANSACTIONS: (id: number) => `/accounts/${id}/transactions/`,
    BALANCE_HISTORY: (id: number) => `/accounts/${id}/balance_history/`,
    RECONCILE: (id: number) => `/accounts/${id}/reconcile/`,
    SUMMARY: '/accounts/summary/',
  },

  // Transactions (transacciones y categorías)
  TRANSACTIONS: {
    BASE: '/transactions/',
    DETAIL: (id: number) => `/transactions/${id}/`,
    BULK: '/transactions/bulk/',
    EXPORT: '/transactions/export/',
  },

  // Categories
  CATEGORIES: {
    BASE: '/categories/',
    DETAIL: (id: number) => `/categories/${id}/`,
    TREE: '/categories/tree/',
    POPULAR: '/categories/popular/',
  },

  // Analytics (reportes y métricas)
  ANALYTICS: {
    BASE: '/analytics/',
    REPORTS: '/analytics/reports/',
    METRICS: '/analytics/metrics/',
    CHARTS: '/analytics/charts/',
    SUMMARY: '/analytics/summary/',
    DASHBOARD: '/analytics/dashboard/',
  },

  // Goals (metas financieras)
  GOALS: {
    BASE: '/goals/',
    DETAIL: (id: number) => `/goals/${id}/`,
    CONTRIBUTIONS: '/goal-contributions/',
    CONTRIBUTION_DETAIL: (id: number) => `/goal-contributions/${id}/`,
    TEMPLATES: '/goal-templates/',
    TEMPLATE_DETAIL: (id: number) => `/goal-templates/${id}/`,
    PROGRESS: '/goals/progress/',
    DASHBOARD: '/goals/dashboard/',
    CREATE_FROM_TEMPLATE: '/goals/create-from-template/',
  },

  // Utilidades comunes
  UTILS: {
    HEALTH: '/health/',
    VERSION: '/version/',
    PING: '/ping/',
  },
} as const;

// Helper function para construir URLs con parámetros
export const buildUrl = (endpoint: string, params?: Record<string, any>): string => {
  if (!params) return endpoint;

  const url = new URL(endpoint, window.location.origin);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.append(key, String(value));
    }
  });

  return url.pathname + url.search;
};

// Tipos para autocompletado
export type AuthEndpoints = typeof API_ENDPOINTS.AUTH;
export type AccountEndpoints = typeof API_ENDPOINTS.ACCOUNTS;
export type TransactionEndpoints = typeof API_ENDPOINTS.TRANSACTIONS;
export type CategoryEndpoints = typeof API_ENDPOINTS.CATEGORIES;
export type AnalyticsEndpoints = typeof API_ENDPOINTS.ANALYTICS;
export type GoalEndpoints = typeof API_ENDPOINTS.GOALS;