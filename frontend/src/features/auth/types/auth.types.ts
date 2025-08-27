// =====================================================
// AUTH TYPES - Alineado 100% con Backend Django
// =====================================================

// Usuario base (Django User model)
export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
}

// Perfil de usuario (UserProfileSerializer)
export interface UserProfile {
  username: string;
  email: string;
  is_demo: boolean;
  demo_expires: string | null;
  created_at: string;
  account_count: number;
  transaction_count: number;
}

// =====================================================
// REQUEST TYPES
// =====================================================

// Login (UserLoginSerializer)
export interface LoginCredentials {
  username: string;
  password: string;
}

// Register (UserRegistrationSerializer)
export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string; // ✅ Corregido: backend usa snake_case
}

// Refresh token request
export interface RefreshTokenRequest {
  refresh: string;
}

// =====================================================
// RESPONSE TYPES
// =====================================================

// JWT Token response (SimpleJWT)
export interface TokenResponse {
  access: string;
  refresh: string;
}

// Register response (register_user view)
export interface RegisterResponse {
  message: string;
  user_id: number;
}

// Demo user response (create_demo_user view)
export interface DemoUserResponse {
  access: string;
  refresh: string;
  demo_user: boolean;
  username: string;
  expires_at: string;
  accounts_created: number;
  transactions_created: number;
}

// Profile response (user_profile view)
export interface ProfileResponse extends UserProfile {}

// =====================================================
// AUTH STATE TYPES
// =====================================================

export interface AuthState {
  isAuthenticated: boolean;
  user: UserProfile | null;
  tokens: {
    access: string | null;
    refresh: string | null;
  };
  isLoading: boolean;
  error: string | null;
  isDemo: boolean;
}

// =====================================================
// HOOK RETURN TYPES
// =====================================================

export interface UseAuthReturn {
  // State
  isAuthenticated: boolean;
  user: UserProfile | null;
  isLoading: boolean;
  error: string | null;
  isDemo: boolean;
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  refreshToken: () => Promise<boolean>;
}

export interface UseProfileReturn {
  // State
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchProfile: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  clearError: () => void;
}

export interface UseDemoReturn {
  // State
  isCreating: boolean;
  error: string | null;
  
  // Actions
  createDemoUser: () => Promise<DemoUserResponse>;
  clearError: () => void;
}

// =====================================================
// ERROR TYPES
// =====================================================

export interface AuthError {
  message: string;
  field?: string;
  code?: string;
  details?: Record<string, string[]>;
}

// Errores específicos de validación
export interface RegisterErrors {
  username?: string[];
  email?: string[];
  password?: string[];
  password_confirm?: string[];
  non_field_errors?: string[];
}

export interface LoginErrors {
  username?: string[];
  password?: string[];
  non_field_errors?: string[];
}

// =====================================================
// UTILITY TYPES
// =====================================================

export interface AuthConfig {
  tokenPrefix: string;
  refreshThreshold: number; // minutos antes de expirar
  demoExpirationHours: number;
  autoRefresh: boolean;
}

export type AuthAction = 
  | 'LOGIN'
  | 'LOGOUT'
  | 'REGISTER'
  | 'REFRESH_TOKEN'
  | 'FETCH_PROFILE'
  | 'CREATE_DEMO'
  | 'CLEAR_ERROR';

// =====================================================
// FORM VALIDATION TYPES
// =====================================================

export interface LoginFormData extends LoginCredentials {}

export interface RegisterFormData extends RegisterData {
  confirmPassword: string; // Para el form (camelCase)
}

// Mapeo de form data a API data
export const mapRegisterFormToApi = (formData: RegisterFormData): RegisterData => ({
  username: formData.username,
  email: formData.email,
  password: formData.password,
  password_confirm: formData.confirmPassword, // Mapeo a snake_case
});

// =====================================================
// CONSTANTS
// =====================================================

export const AUTH_STORAGE_KEYS = {
  ACCESS_TOKEN: 'fintrack_access_token',
  REFRESH_TOKEN: 'fintrack_refresh_token',
  USER_PROFILE: 'fintrack_user_profile',
} as const;

export const AUTH_ENDPOINTS = {
  LOGIN: '/token/',                    // JWT login
  REFRESH: '/token/refresh/',          // JWT refresh
  REGISTER: '/auth/register/',         // Custom register
  DEMO: '/auth/demo/',                 // Demo user
  PROFILE: '/auth/profile/',           // User profile
} as const;

export const DEMO_CONFIG = {
  DEFAULT_DURATION_HOURS: 24,
  WARNING_THRESHOLD_HOURS: 2,
  AUTO_EXTEND: false,
} as const;