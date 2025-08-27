// Tipos base de API
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
  success: boolean;
}

// Respuesta paginada (formato DRF estándar)
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Error de API (compatible con DRF)
export interface ApiError {
  message: string;
  errors?: Record<string, string[]>; // Errores de validación DRF
  status?: number;
  code?: string;
  detail?: string; // Campo estándar de DRF para errores
}

// Tipos de filtros comunes
export interface DateRangeFilter {
  start_date?: string;
  end_date?: string;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

// Tipos para ordenamiento
export interface OrderingParams {
  ordering?: string; // Ej: '-created_at', 'name'
}

// Filtros base que usa DRF
export interface BaseFilterParams extends PaginationParams, OrderingParams {
  search?: string;
}

// Estados de carga
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

// Opciones de API comunes
export interface ApiOptions {
  immediate?: boolean;
  cache?: boolean;
  retries?: number;
  onSuccess?: (data: any) => void;
  onError?: (error: ApiError) => void;
}

// Respuesta de autenticación JWT (DRF SimpleJWT)
export interface TokenResponse {
  access: string;
  refresh: string;
}

// Respuesta de refresh token
export interface RefreshTokenResponse {
  access: string;
}

// Tipos para endpoints específicos de FinTrack
export interface EndpointUrls {
  // Auth
  login: string;
  refresh: string;
  register: string;
  profile: string;
  
  // Accounts
  accounts: string;
  accountDetail: (id: number) => string;
  accountTransactions: (id: number) => string;
  accountBalanceHistory: (id: number) => string;
  accountReconcile: (id: number) => string;
  accountSummary: string;
  
  // Transactions
  transactions: string;
  transactionDetail: (id: number) => string;
  categories: string;
  categoryDetail: (id: number) => string;
  
  // Analytics
  reports: string;
  metrics: string;
  alerts: string;
  
  // Goals
  goals: string;
  goalDetail: (id: number) => string;
  goalContributions: string;
  goalTemplates: string;
  goalProgress: string;
}

// Configuración de ambiente
export interface EnvironmentConfig {
  API_URL: string;
  API_TIMEOUT: number;
  DEBUG: boolean;
  VERSION: string;
}

// Metadatos de respuesta
export interface ResponseMetadata {
  timestamp: string;
  version: string;
  request_id?: string;
}

// Tipos para caché
export interface CacheConfig {
  enabled: boolean;
  ttl: number; // Time to live en segundos
  key: string;
}

// Configuración de retry
export interface RetryConfig {
  attempts: number;
  delay: number;
  backoff?: boolean;
}