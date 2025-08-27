// =====================================================
// AUTH API SERVICES - Servicios específicos de autenticación
// Usa el cliente genérico para llamadas específicas de auth
// =====================================================

import apiClient from '@/services/api/client';
import {
  LoginCredentials,
  RegisterData,
  RefreshTokenRequest,
  TokenResponse,
  RegisterResponse,
  DemoUserResponse,
  ProfileResponse,
  AUTH_ENDPOINTS,
} from '../types/auth.types';
import { ApiError } from '@/types/api.types';

// =====================================================
// AUTHENTICATION API
// =====================================================

export const authApi = {
  /**
   * Login - Obtener tokens JWT
   * POST /api/token/
   */
  login: async (credentials: LoginCredentials): Promise<TokenResponse> => {
    try {
      const response = await apiClient.post<TokenResponse>(
        AUTH_ENDPOINTS.LOGIN,
        credentials
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Register - Crear nueva cuenta
   * POST /api/auth/register/
   */
  register: async (userData: RegisterData): Promise<RegisterResponse> => {
    try {
      const response = await apiClient.post<RegisterResponse>(
        AUTH_ENDPOINTS.REGISTER,
        userData
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Refresh Token - Renovar access token
   * POST /api/token/refresh/
   */
  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    try {
      const request: RefreshTokenRequest = { refresh: refreshToken };
      const response = await apiClient.post<TokenResponse>(
        AUTH_ENDPOINTS.REFRESH,
        request
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Create Demo User - Crear usuario demo con datos
   * POST /api/auth/demo/
   */
  createDemo: async (): Promise<DemoUserResponse> => {
    try {
      const response = await apiClient.post<DemoUserResponse>(
        AUTH_ENDPOINTS.DEMO,
        {} // No requiere datos
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get User Profile - Obtener perfil del usuario
   * GET /api/auth/profile/
   */
  getProfile: async (): Promise<ProfileResponse> => {
    try {
      const response = await apiClient.get<ProfileResponse>(
        AUTH_ENDPOINTS.PROFILE
      );
      return response;
    } catch (error) {
      throw error;
    }
  },
};

// =====================================================
// AUTH UTILITIES
// =====================================================

export const authUtils = {
  /**
   * Validar si el demo ha expirado
   */
  isDemoExpired: (expiresAt: string | null): boolean => {
    if (!expiresAt) return false;
    return new Date() > new Date(expiresAt);
  },

  /**
   * Calcular tiempo restante del demo
   */
  getDemoTimeRemaining: (expiresAt: string | null): number => {
    if (!expiresAt) return 0;
    const now = new Date().getTime();
    const expires = new Date(expiresAt).getTime();
    return Math.max(0, expires - now);
  },

  /**
   * Formatear tiempo restante del demo
   */
  formatDemoTimeRemaining: (expiresAt: string | null): string => {
    const timeRemaining = authUtils.getDemoTimeRemaining(expiresAt);
    
    if (timeRemaining === 0) return 'Expirado';
    
    const hours = Math.floor(timeRemaining / (1000 * 60 * 60));
    const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}h ${minutes}m restantes`;
    }
    return `${minutes}m restantes`;
  },

  /**
   * Extraer información del token (sin verificación, solo parsing)
   */
  parseTokenPayload: (token: string): any => {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        window.atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('Error parsing token:', error);
      return null;
    }
  },

  /**
   * Verificar si el token está cerca de expirar
   */
  isTokenNearExpiry: (token: string, thresholdMinutes: number = 5): boolean => {
    const payload = authUtils.parseTokenPayload(token);
    if (!payload || !payload.exp) return true;
    
    const now = Date.now() / 1000;
    const threshold = thresholdMinutes * 60;
    
    return (payload.exp - now) < threshold;
  },

  /**
   * Validar formato de email
   */
  isValidEmail: (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  /**
   * Validar fortaleza de contraseña
   */
  validatePassword: (password: string): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];
    
    if (password.length < 8) {
      errors.push('La contraseña debe tener al menos 8 caracteres');
    }
    
    if (!/[a-z]/.test(password)) {
      errors.push('Debe contener al menos una letra minúscula');
    }
    
    if (!/[A-Z]/.test(password)) {
      errors.push('Debe contener al menos una letra mayúscula');
    }
    
    if (!/\d/.test(password)) {
      errors.push('Debe contener al menos un número');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
    };
  },
};

// =====================================================
// ERROR HANDLERS ESPECÍFICOS
// =====================================================

export const authErrorHandlers = {
  /**
   * Manejar errores de login
   */
  handleLoginError: (error: ApiError): string => {
    if (error.status === 401) {
      return 'Credenciales inválidas. Verifica tu usuario y contraseña.';
    }
    
    if (error.errors?.non_field_errors) {
      return error.errors.non_field_errors[0];
    }
    
    return error.message || 'Error al iniciar sesión';
  },

  /**
   * Manejar errores de registro
   */
  handleRegisterError: (error: ApiError): Record<string, string> => {
    const fieldErrors: Record<string, string> = {};
    
    if (error.errors) {
      Object.entries(error.errors).forEach(([field, messages]) => {
        fieldErrors[field] = Array.isArray(messages) ? messages[0] : messages;
      });
    } else {
      fieldErrors.general = error.message || 'Error al crear la cuenta';
    }
    
    return fieldErrors;
  },

  /**
   * Manejar errores de demo
   */
  handleDemoError: (error: ApiError): string => {
    if (error.status === 500) {
      return 'Error interno del servidor. Intenta más tarde.';
    }
    
    return error.message || 'Error al crear usuario demo';
  },

  /**
   * Manejar errores de perfil
   */
  handleProfileError: (error: ApiError): string => {
    if (error.status === 401) {
      return 'Sesión expirada. Por favor, inicia sesión nuevamente.';
    }
    
    return error.message || 'Error al cargar el perfil';
  },
};

// =====================================================
// EXPORT DEFAULT
// =====================================================

export default authApi;