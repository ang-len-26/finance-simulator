// =====================================================
// API TYPES - Tipos base de API (sin endpoints duplicados)
// Los endpoints ahora están en @/services/api/endpoints.ts
// =====================================================

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

// =====================================================
// FILTER TYPES
// =====================================================

// Tipos de filtros comunes
export interface DateRangeFilter {
  start_date?: string;
  end_date?: string;
  date_after?: string;
  date_before?: string;
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

// =====================================================
// LOADING & STATE TYPES
// =====================================================

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

// =====================================================
// JWT TOKEN TYPES
// =====================================================

// Respuesta de autenticación JWT (DRF SimpleJWT)
export interface TokenResponse {
  access: string;
  refresh: string;
}

// Respuesta de refresh token
export interface RefreshTokenResponse {
  access: string;
}

// =====================================================
// ENVIRONMENT & CONFIG TYPES
// =====================================================

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

// =====================================================
// CACHE & RETRY TYPES
// =====================================================

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

// =====================================================
// API CLIENT TYPES
// =====================================================

// Configuración del cliente API
export interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  retries: RetryConfig;
  cache: CacheConfig;
  auth: {
    tokenPrefix: string;
    refreshThreshold: number;
  };
}

// Request configuration
export interface RequestConfig {
  headers?: Record<string, string>;
  params?: Record<string, any>;
  timeout?: number;
  retries?: number;
  cache?: boolean;
}

// =====================================================
// BUSINESS LOGIC TYPES
// =====================================================

// Tipos de datos monetarios
export interface MoneyAmount {
  amount: string; // Decimal como string para precisión
  currency: string; // 'PEN', 'USD', etc.
}

// Rango de fechas para filtros
export interface DateRange {
  from: Date | string;
  to: Date | string;
}

// Tipos de período para reportes
export type ReportPeriod = 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly' | 'custom';

// Filtros de transacciones
export interface TransactionFilters extends BaseFilterParams {
  account_id?: number;
  category_id?: number;
  transaction_type?: 'income' | 'expense' | 'transfer';
  amount_min?: number;
  amount_max?: number;
  date_range?: DateRangeFilter;
}

// Filtros de cuentas
export interface AccountFilters extends BaseFilterParams {
  account_type?: 'checking' | 'savings' | 'credit' | 'cash' | 'investment';
  is_active?: boolean;
  balance_min?: number;
  balance_max?: number;
}

// =====================================================
// FORM & VALIDATION TYPES
// =====================================================

// Estado de validación de formularios
export interface ValidationState {
  isValid: boolean;
  errors: Record<string, string[]>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
}

// Resultado de validación de campo
export interface FieldValidation {
  isValid: boolean;
  error?: string;
  warning?: string;
}

// =====================================================
// UTILITY TYPES
// =====================================================

// Tipo para IDs de recursos
export type ResourceId = number | string;

// Tipo para timestamps
export type Timestamp = string; // ISO 8601 format

// Tipo para status de recursos
export type ResourceStatus = 'active' | 'inactive' | 'pending' | 'archived';

// Acción genérica de API
export type ApiAction = 'create' | 'read' | 'update' | 'delete' | 'list';

// Resultado de operación CRUD
export interface CrudResult<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  action: ApiAction;
}
