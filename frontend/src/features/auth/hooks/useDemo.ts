// =====================================================
// useDemo Hook - Gestión específica de usuarios demo
// Creación, gestión y cleanup de usuarios demo
// =====================================================

import { useState, useCallback, useEffect } from 'react';
import { authApi, authErrorHandlers, authUtils } from '../services/authApi';
import { setTokens, clearTokens } from '@/services/api/client';
import {
  DemoUserResponse,
  UseDemoReturn,
  AUTH_STORAGE_KEYS,
  DEMO_CONFIG,
} from '../types/auth.types';
import { ApiError } from '@/types/api.types';

// =====================================================
// useDemo HOOK
// =====================================================

export const useDemo = (): UseDemoReturn => {
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // =====================================================
  // ACTIONS
  // =====================================================

  /**
   * Create Demo User - Crear usuario demo con datos completos
   */
  const createDemoUser = useCallback(async (): Promise<DemoUserResponse> => {
    setIsCreating(true);
    setError(null);
    
    try {
      console.log('🎭 Creating demo user...');
      
      // 1. Crear usuario demo
      const demoResponse = await authApi.createDemo();
      
      // 2. Guardar tokens automáticamente
      setTokens(demoResponse.access, demoResponse.refresh);
      
      // 3. Crear perfil demo para localStorage
      const demoProfile = {
        username: demoResponse.username,
        email: `${demoResponse.username}@demo.fintrack.com`,
        is_demo: true,
        demo_expires: demoResponse.expires_at,
        created_at: new Date().toISOString(),
        account_count: demoResponse.accounts_created,
        transaction_count: demoResponse.transactions_created,
      };
      
      // 4. Guardar perfil en localStorage
      localStorage.setItem(
        AUTH_STORAGE_KEYS.USER_PROFILE,
        JSON.stringify(demoProfile)
      );
      
      console.log('✅ Demo user created successfully:', {
        username: demoResponse.username,
        accounts: demoResponse.accounts_created,
        transactions: demoResponse.transactions_created,
        expiresAt: demoResponse.expires_at,
      });
      
      return demoResponse;
      
    } catch (error) {
      const errorMessage = authErrorHandlers.handleDemoError(error as ApiError);
      setError(errorMessage);
      console.error('❌ Failed to create demo user:', error);
      throw error;
    } finally {
      setIsCreating(false);
    }
  }, []);

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
   * Auto-clear error después de 10 segundos
   */
  useEffect(() => {
    if (!error) return;
    
    const timeout = setTimeout(() => {
      clearError();
    }, 10000);
    
    return () => clearTimeout(timeout);
  }, [error, clearError]);

  // =====================================================
  // RETURN
  // =====================================================

  return {
    // State
    isCreating,
    error,
    
    // Actions
    createDemoUser,
    clearError,
  };
};

// =====================================================
// DEMO UTILITY HOOKS
// =====================================================

/**
 * Hook para gestionar expiración de demo
 */
export const useDemoExpiration = (expiresAt: string | null) => {
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [isExpired, setIsExpired] = useState(false);

  useEffect(() => {
    if (!expiresAt) return;

    const updateTime = () => {
      const remaining = authUtils.getDemoTimeRemaining(expiresAt);
      setTimeRemaining(remaining);
      setIsExpired(remaining === 0);
    };

    // Actualizar inmediatamente
    updateTime();

    // Actualizar cada minuto
    const interval = setInterval(updateTime, 60000);

    return () => clearInterval(interval);
  }, [expiresAt]);

  const hoursRemaining = Math.floor(timeRemaining / (1000 * 60 * 60));
  const minutesRemaining = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));

  return {
    timeRemaining,
    isExpired,
    hoursRemaining,
    minutesRemaining,
    formattedTime: authUtils.formatDemoTimeRemaining(expiresAt),
    isNearExpiry: hoursRemaining < DEMO_CONFIG.WARNING_THRESHOLD_HOURS,
  };
};

/**
 * Hook para notificaciones de demo
 */
export const useDemoNotifications = (expiresAt: string | null) => {
  const { isNearExpiry, isExpired, formattedTime } = useDemoExpiration(expiresAt);
  const [hasShownWarning, setHasShownWarning] = useState(false);
  const [hasShownExpired, setHasShownExpired] = useState(false);

  useEffect(() => {
    if (isExpired && !hasShownExpired) {
      setHasShownExpired(true);
      // Aquí podrías mostrar una notificación de expiración
      console.log('🔔 Demo expired notification');
    } else if (isNearExpiry && !hasShownWarning) {
      setHasShownWarning(true);
      // Aquí podrías mostrar una notificación de advertencia
      console.log('⚠️ Demo expiring soon notification:', formattedTime);
    }
  }, [isExpired, isNearExpiry, hasShownExpired, hasShownWarning, formattedTime]);

  return {
    shouldShowWarning: isNearExpiry && !isExpired,
    shouldShowExpired: isExpired,
    warningMessage: `Tu demo expira en ${formattedTime}`,
    expiredMessage: 'Tu demo ha expirado. ¡Crea una cuenta para continuar!',
  };
};

/**
 * Hook para estadísticas del demo
 */
export const useDemoStats = (demoData?: DemoUserResponse) => {
  if (!demoData) {
    return {
      accountsCreated: 0,
      transactionsCreated: 0,
      demoUsername: '',
      hasData: false,
    };
  }

  return {
    accountsCreated: demoData.accounts_created,
    transactionsCreated: demoData.transactions_created,
    demoUsername: demoData.username,
    hasData: true,
    dataQuality: demoData.accounts_created > 0 && demoData.transactions_created > 0 ? 'good' : 'limited',
  };
};

/**
 * Hook para conversión de demo a cuenta real
 */
export const useDemoToAccount = () => {
  const [isConverting, setIsConverting] = useState(false);
  const [conversionError, setConversionError] = useState<string | null>(null);

  const convertToRealAccount = useCallback(async (userData: {
    email: string;
    password: string;
    password_confirm: string;
  }) => {
    setIsConverting(true);
    setConversionError(null);

    try {
      // Esta funcionalidad requeriría un endpoint específico en el backend
      // Por ahora, sugerimos al usuario crear una cuenta nueva
      console.log('🔄 Converting demo to real account...', userData);
      
      // Placeholder - en el futuro implementar conversión real
      throw new Error('Funcionalidad en desarrollo. Por favor, crea una cuenta nueva.');
      
    } catch (error) {
      setConversionError((error as Error).message);
      throw error;
    } finally {
      setIsConverting(false);
    }
  }, []);

  return {
    isConverting,
    conversionError,
    convertToRealAccount,
    clearError: () => setConversionError(null),
  };
};

/**
 * Hook para cleanup de demo
 */
export const useDemoCleanup = () => {
  const cleanupDemo = useCallback(() => {
    // Limpiar tokens
    clearTokens();
    
    // Limpiar localStorage
    localStorage.removeItem(AUTH_STORAGE_KEYS.USER_PROFILE);
    
    // Limpiar cualquier otro estado relacionado con demo
    console.log('🧹 Demo cleanup completed');
  }, []);

  return { cleanupDemo };
};

export default useDemo;