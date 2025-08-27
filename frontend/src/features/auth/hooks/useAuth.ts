// =====================================================
// useAuth Hook - Hook principal de autenticación
// Maneja estado global de auth, login, register, logout
// =====================================================

import { useState, useEffect, useCallback } from 'react';
import { authApi, authErrorHandlers, authUtils } from '../services/authApi';
import {
  setTokens,
  clearTokens,
  getAccessToken,
  getRefreshToken,
  isAuthenticated as checkIsAuthenticated,
} from '@/services/api/client';
import {
  LoginCredentials,
  RegisterData,
  UserProfile,
  UseAuthReturn,
  AuthState,
  AUTH_STORAGE_KEYS,
} from '../types/auth.types';
import { ApiError } from '@/types/api.types';

// =====================================================
// INITIAL STATE
// =====================================================

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  tokens: {
    access: null,
    refresh: null,
  },
  isLoading: false,
  error: null,
  isDemo: false,
};

// =====================================================
// useAuth HOOK
// =====================================================

export const useAuth = (): UseAuthReturn => {
  const [state, setState] = useState<AuthState>(() => {
    // Inicializar desde localStorage al montar
    const savedProfile = localStorage.getItem(AUTH_STORAGE_KEYS.USER_PROFILE);
    const isAuth = checkIsAuthenticated();
    
    if (isAuth && savedProfile) {
      const profile = JSON.parse(savedProfile);
      return {
        ...initialState,
        isAuthenticated: true,
        user: profile,
        tokens: {
          access: getAccessToken(),
          refresh: getRefreshToken(),
        },
        isDemo: profile.is_demo,
      };
    }
    
    return initialState;
  });

  // =====================================================
  // ACTIONS
  // =====================================================

  /**
   * Login - Autenticar usuario
   */
  const login = useCallback(async (credentials: LoginCredentials): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      // 1. Obtener tokens
      const tokenResponse = await authApi.login(credentials);
      
      // 2. Guardar tokens
      setTokens(tokenResponse.access, tokenResponse.refresh);
      
      // 3. Obtener perfil del usuario
      const profileResponse = await authApi.getProfile();
      
      // 4. Guardar perfil en localStorage
      localStorage.setItem(
        AUTH_STORAGE_KEYS.USER_PROFILE,
        JSON.stringify(profileResponse)
      );
      
      // 5. Actualizar estado
      setState({
        isAuthenticated: true,
        user: profileResponse,
        tokens: {
          access: tokenResponse.access,
          refresh: tokenResponse.refresh,
        },
        isLoading: false,
        error: null,
        isDemo: profileResponse.is_demo,
      });
      
      console.log('✅ Login successful:', credentials.username);
      
    } catch (error) {
      const errorMessage = authErrorHandlers.handleLoginError(error as ApiError);
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  }, []);

  /**
   * Register - Crear nueva cuenta
   */
  const register = useCallback(async (userData: RegisterData): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      // 1. Registrar usuario
      const registerResponse = await authApi.register(userData);
      console.log('✅ User registered:', registerResponse.message);
      
      // 2. Auto-login después del registro
      await login({
        username: userData.username,
        password: userData.password,
      });
      
    } catch (error) {
      const errorFields = authErrorHandlers.handleRegisterError(error as ApiError);
      const errorMessage = errorFields.general || 'Error al crear la cuenta';
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  }, [login]);

  /**
   * Logout - Cerrar sesión
   */
  const logout = useCallback((): void => {
    // 1. Limpiar tokens
    clearTokens();
    
    // 2. Limpiar localStorage
    localStorage.removeItem(AUTH_STORAGE_KEYS.USER_PROFILE);
    
    // 3. Resetear estado
    setState(initialState);
    
    console.log('✅ Logout successful');
    
    // 4. Redireccionar a login (opcional)
    // window.location.href = '/auth/login';
  }, []);

  /**
   * Refresh Token - Renovar access token
   */
  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const refreshTokenValue = getRefreshToken();
      if (!refreshTokenValue) {
        throw new Error('No refresh token available');
      }
      
      const response = await authApi.refreshToken(refreshTokenValue);
      
      // Actualizar tokens
      setTokens(response.access, refreshTokenValue);
      
      setState(prev => ({
        ...prev,
        tokens: {
          access: response.access,
          refresh: refreshTokenValue,
        },
      }));
      
      console.log('✅ Token refreshed successfully');
      return true;
      
    } catch (error) {
      console.error('❌ Token refresh failed:', error);
      logout(); // Auto-logout si falla el refresh
      return false;
    }
  }, [logout]);

  /**
   * Clear Error - Limpiar error
   */
  const clearError = useCallback((): void => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // =====================================================
  // EFFECTS
  // =====================================================

  /**
   * Auto-refresh token cuando esté cerca de expirar
   */
  useEffect(() => {
    if (!state.isAuthenticated || !state.tokens.access) return;
    
    const token = state.tokens.access;
    
    // Verificar cada 5 minutos si el token está cerca de expirar
    const interval = setInterval(() => {
      if (authUtils.isTokenNearExpiry(token, 10)) { // 10 min threshold
        console.log('🔄 Token near expiry, refreshing...');
        refreshToken();
      }
    }, 5 * 60 * 1000); // 5 minutos
    
    return () => clearInterval(interval);
  }, [state.isAuthenticated, state.tokens.access, refreshToken]);

  /**
   * Verificar si el demo ha expirado
   */
  useEffect(() => {
    if (!state.isDemo || !state.user?.demo_expires) return;
    
    const checkDemoExpiry = () => {
      if (authUtils.isDemoExpired(state.user!.demo_expires)) {
        console.log('⏰ Demo expired, logging out...');
        logout();
      }
    };
    
    // Verificar inmediatamente
    checkDemoExpiry();
    
    // Verificar cada minuto
    const interval = setInterval(checkDemoExpiry, 60 * 1000);
    
    return () => clearInterval(interval);
  }, [state.isDemo, state.user?.demo_expires, logout]);

  /**
   * Limpiar error automáticamente después de 10 segundos
   */
  useEffect(() => {
    if (!state.error) return;
    
    const timeout = setTimeout(() => {
      clearError();
    }, 10 * 1000);
    
    return () => clearTimeout(timeout);
  }, [state.error, clearError]);

  // =====================================================
  // RETURN
  // =====================================================

  return {
    // State
    isAuthenticated: state.isAuthenticated,
    user: state.user,
    isLoading: state.isLoading,
    error: state.error,
    isDemo: state.isDemo,
    
    // Actions
    login,
    register,
    logout,
    clearError,
    refreshToken,
  };
};

// =====================================================
// UTILITY HOOKS
// =====================================================

/**
 * Hook simple para verificar autenticación
 */
export const useIsAuthenticated = (): boolean => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated;
};

/**
 * Hook para obtener usuario actual
 */
export const useCurrentUser = (): UserProfile | null => {
  const { user } = useAuth();
  return user;
};

/**
 * Hook para verificar si es usuario demo
 */
export const useIsDemo = (): boolean => {
  const { isDemo } = useAuth();
  return isDemo;
};

/**
 * Hook para obtener tiempo restante del demo
 */
export const useDemoTimeRemaining = (): string => {
  const { user, isDemo } = useAuth();
  
  if (!isDemo || !user?.demo_expires) return '';
  
  return authUtils.formatDemoTimeRemaining(user.demo_expires);
};

export default useAuth;