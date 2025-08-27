// =====================================================
// useProfile Hook - Gestión específica del perfil
// Separado de useAuth para responsabilidades específicas
// =====================================================

import { useState, useCallback, useEffect } from 'react';
import { authApi, authErrorHandlers } from '../services/authApi';
import {
  UserProfile,
  UseProfileReturn,
  AUTH_STORAGE_KEYS,
} from '../types/auth.types';
import { ApiError } from '@/types/api.types';

// =====================================================
// useProfile HOOK
// =====================================================

export const useProfile = (): UseProfileReturn => {
  const [profile, setProfile] = useState<UserProfile | null>(() => {
    // Inicializar desde localStorage
    const saved = localStorage.getItem(AUTH_STORAGE_KEYS.USER_PROFILE);
    return saved ? JSON.parse(saved) : null;
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // =====================================================
  // ACTIONS
  // =====================================================

  /**
   * Fetch Profile - Obtener perfil del servidor
   */
  const fetchProfile = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const profileData = await authApi.getProfile();
      
      // Actualizar estado
      setProfile(profileData);
      
      // Guardar en localStorage
      localStorage.setItem(
        AUTH_STORAGE_KEYS.USER_PROFILE,
        JSON.stringify(profileData)
      );
      
      console.log('✅ Profile fetched successfully');
      
    } catch (error) {
      const errorMessage = authErrorHandlers.handleProfileError(error as ApiError);
      setError(errorMessage);
      console.error('❌ Failed to fetch profile:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Refresh Profile - Refrescar datos del perfil
   */
  const refreshProfile = useCallback(async (): Promise<void> => {
    // Similar a fetchProfile pero sin loading inicial
    await fetchProfile();
  }, [fetchProfile]);

  /**
   * Clear Error - Limpiar error
   */
  const clearError = useCallback((): void => {
    setError(null);
  }, []);

  // =====================================================
  // EFFECTS
  // =====================================================

  /**
   * Auto-clear error después de 8 segundos
   */
  useEffect(() => {
    if (!error) return;
    
    const timeout = setTimeout(() => {
      clearError();
    }, 8000);
    
    return () => clearTimeout(timeout);
  }, [error, clearError]);

  // =====================================================
  // RETURN
  // =====================================================

  return {
    // State
    profile,
    isLoading,
    error,
    
    // Actions
    fetchProfile,
    refreshProfile,
    clearError,
  };
};

// =====================================================
// SPECIALIZED PROFILE HOOKS
// =====================================================

/**
 * Hook para estadísticas del usuario
 */
export const useUserStats = () => {
  const { profile } = useProfile();
  
  return {
    accountCount: profile?.account_count || 0,
    transactionCount: profile?.transaction_count || 0,
    isDemo: profile?.is_demo || false,
    memberSince: profile?.created_at ? new Date(profile.created_at) : null,
  };
};

/**
 * Hook para información del demo
 */
export const useDemoInfo = () => {
  const { profile } = useProfile();
  
  if (!profile?.is_demo) {
    return {
      isDemo: false,
      expiresAt: null,
      timeRemaining: null,
      isExpired: false,
    };
  }
  
  const expiresAt = profile.demo_expires ? new Date(profile.demo_expires) : null;
  const now = new Date();
  const isExpired = expiresAt ? now > expiresAt : false;
  const timeRemaining = expiresAt ? Math.max(0, expiresAt.getTime() - now.getTime()) : 0;
  
  return {
    isDemo: true,
    expiresAt,
    timeRemaining,
    isExpired,
    hoursRemaining: Math.floor(timeRemaining / (1000 * 60 * 60)),
    minutesRemaining: Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60)),
  };
};

/**
 * Hook para validar perfil completo
 */
export const useProfileValidation = () => {
  const { profile } = useProfile();
  
  const validation = {
    hasEmail: Boolean(profile?.email),
    hasUsername: Boolean(profile?.username),
    hasActivity: (profile?.transaction_count || 0) > 0,
    hasAccounts: (profile?.account_count || 0) > 0,
  };
  
  const completionScore = Object.values(validation).filter(Boolean).length;
  const isComplete = completionScore === Object.keys(validation).length;
  
  return {
    validation,
    completionScore,
    isComplete,
    completionPercentage: (completionScore / Object.keys(validation).length) * 100,
  };
};

export default useProfile;