// =====================================================
// useBudgetAlerts - Hook para gestión de alertas de presupuesto
// Basado en BudgetAlertViewSet del backend
// Subrama 3.2 - Transactions Hooks
// =====================================================

import { useState, useCallback, useEffect } from 'react';
import { useAsyncState } from '@/hooks/useAsyncState';
import { transactionsApi } from '../services/transactionsApi';
import { BudgetAlert, UnreadAlertsResult } from '../types/transactions.types';
import { PaginatedResponse, ApiError } from '@/types/api.types';

// =====================================================
// TIPOS INTERNOS DEL HOOK
// =====================================================

interface UseBudgetAlertsState {
  alerts: BudgetAlert[];
  unreadAlerts: BudgetAlert[];
  selectedAlert: BudgetAlert | null;
  totalCount: number;
  unreadCount: number;
  hasNewAlerts: boolean;
}

interface UseBudgetAlertsOptions {
  autoLoad?: boolean;
  pollInterval?: number; // Intervalo para polling automático (en ms)
  onNewAlert?: (alert: BudgetAlert) => void; // Callback cuando hay nueva alerta
}

interface UseBudgetAlertsReturn {
  // Estado principal
  data: UseBudgetAlertsState;
  isLoading: boolean;
  error: ApiError | null;
  
  // Operaciones básicas
  loadAlerts: () => Promise<void>;
  loadUnreadAlerts: () => Promise<UnreadAlertsResult>;
  getAlert: (id: number) => Promise<BudgetAlert>;
  markAsRead: (id: number) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  
  // Utilidades
  refreshAlerts: () => Promise<void>;
  clearError: () => void;
  setSelectedAlert: (alert: BudgetAlert | null) => void;
  
  // Filtros y helpers
  getAlertsByType: (alertType: string) => BudgetAlert[];
  getAlertsBySeverity: (severity: 'info' | 'warning' | 'error') => BudgetAlert[];
  getRecentAlerts: (hours?: number) => BudgetAlert[];
  
  // Control de polling
  startPolling: () => void;
  stopPolling: () => void;
  isPolling: boolean;
}

// =====================================================
// HOOK PRINCIPAL
// =====================================================

export const useBudgetAlerts = (options: UseBudgetAlertsOptions = {}): UseBudgetAlertsReturn => {
  const {
    autoLoad = true,
    pollInterval = 60000, // 1 minuto por defecto
    onNewAlert
  } = options;

  // Estado principal usando useAsyncState
  const {
    data: asyncData,
    isLoading,
    error,
    execute,
    clearError
  } = useAsyncState<PaginatedResponse<BudgetAlert>>();

  // Estado local del hook
  const [state, setState] = useState<UseBudgetAlertsState>({
    alerts: [],
    unreadAlerts: [],
    selectedAlert: null,
    totalCount: 0,
    unreadCount: 0,
    hasNewAlerts: false
  });

  // Estado de polling
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  // =====================================================
  // OPERACIONES BÁSICAS
  // =====================================================

  const loadAlerts = useCallback(async () => {
    const result = await execute(() => transactionsApi.getBudgetAlerts());
    
    if (result) {
      const previousUnreadCount = state.unreadCount;
      const newUnreadAlerts = result.results.filter(alert => !alert.is_read);
      
      setState(prev => ({
        ...prev,
        alerts: result.results,
        totalCount: result.count,
        unreadAlerts: newUnreadAlerts,
        unreadCount: newUnreadAlerts.length,
        hasNewAlerts: newUnreadAlerts.length > previousUnreadCount
      }));

      // Notificar nuevas alertas si hay callback
      if (onNewAlert && newUnreadAlerts.length > previousUnreadCount) {
        const newAlerts = newUnreadAlerts.slice(0, newUnreadAlerts.length - previousUnreadCount);
        newAlerts.forEach(alert => onNewAlert(alert));
      }
    }
  }, [execute, state.unreadCount, onNewAlert]);

  const loadUnreadAlerts = useCallback(async (): Promise<UnreadAlertsResult> => {
    const result = await transactionsApi.getUnreadAlerts();
    
    setState(prev => ({
      ...prev,
      unreadAlerts: result.unread_alerts,
      unreadCount: result.count,
      hasNewAlerts: result.count > prev.unreadCount
    }));

    return result;
  }, []);

  const getAlert = useCallback(async (id: number): Promise<BudgetAlert> => {
    const alert = await transactionsApi.getBudgetAlert(id);
    
    setState(prev => ({
      ...prev,
      selectedAlert: alert
    }));

    return alert;
  }, []);

  const markAsRead = useCallback(async (id: number): Promise<void> => {
    await transactionsApi.markAlertAsRead(id);
    
    // Actualizar estado local
    setState(prev => ({
      ...prev,
      alerts: prev.alerts.map(alert => 
        alert.id === id ? { ...alert, is_read: true } : alert
      ),
      unreadAlerts: prev.unreadAlerts.filter(alert => alert.id !== id),
      unreadCount: Math.max(0, prev.unreadCount - 1),
      selectedAlert: prev.selectedAlert?.id === id 
        ? { ...prev.selectedAlert, is_read: true } 
        : prev.selectedAlert
    }));
  }, []);

  const markAllAsRead = useCallback(async (): Promise<void> => {
    // Marcar todas las alertas no leídas como leídas
    const markPromises = state.unreadAlerts.map(alert => 
      transactionsApi.markAlertAsRead(alert.id)
    );
    
    await Promise.all(markPromises);
    
    // Actualizar estado local
    setState(prev => ({
      ...prev,
      alerts: prev.alerts.map(alert => ({ ...alert, is_read: true })),
      unreadAlerts: [],
      unreadCount: 0,
      hasNewAlerts: false
    }));
  }, [state.unreadAlerts]);

  // =====================================================
  // UTILIDADES
  // =====================================================

  const refreshAlerts = useCallback(async () => {
    await loadAlerts();
  }, [loadAlerts]);

  const setSelectedAlert = useCallback((alert: BudgetAlert | null) => {
    setState(prev => ({
      ...prev,
      selectedAlert: alert
    }));
  }, []);

  // =====================================================
  // FILTROS Y HELPERS
  // =====================================================

  const getAlertsByType = useCallback((alertType: string): BudgetAlert[] => {
    return state.alerts.filter(alert => alert.alert_type === alertType);
  }, [state.alerts]);

  const getAlertsBySeverity = useCallback((severity: 'info' | 'warning' | 'error'): BudgetAlert[] => {
    return state.alerts.filter(alert => alert.severity === severity);
  }, [state.alerts]);

  const getRecentAlerts = useCallback((hours: number = 24): BudgetAlert[] => {
    const cutoffTime = new Date();
    cutoffTime.setHours(cutoffTime.getHours() - hours);
    
    return state.alerts.filter(alert => 
      new Date(alert.created_at) >= cutoffTime
    );
  }, [state.alerts]);

  // =====================================================
  // CONTROL DE POLLING
  // =====================================================

  const startPolling = useCallback(() => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }

    const interval = setInterval(async () => {
      try {
        await loadUnreadAlerts();
      } catch (error) {
        console.warn('Error al verificar alertas:', error);
      }
    }, pollInterval);

    setPollingInterval(interval);
    setIsPolling(true);
  }, [pollingInterval, pollInterval, loadUnreadAlerts]);

  const stopPolling = useCallback(() => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
    setIsPolling(false);
  }, [pollingInterval]);

  // =====================================================
  // EFECTOS
  // =====================================================

  useEffect(() => {
    if (autoLoad) {
      loadAlerts();
    }
  }, [autoLoad]);

  // Cleanup del polling al desmontar
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  // =====================================================
  // HOOKS PERSONALIZADOS ADICIONALES
  // =====================================================

  // Hook para notificaciones del navegador
  const requestNotificationPermission = useCallback(async (): Promise<boolean> => {
    if (!('Notification' in window)) {
      console.warn('Este navegador no soporta notificaciones');
      return false;
    }

    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }, []);

  const showBrowserNotification = useCallback((alert: BudgetAlert) => {
    if (Notification.permission === 'granted') {
      const notification = new Notification(`FinTrack - ${alert.title}`, {
        body: alert.message,
        icon: '/favicon.ico',
        tag: `alert-${alert.id}`,
        requireInteraction: alert.severity === 'error'
      });

      // Auto-cerrar después de 5 segundos para alertas de info y warning
      if (alert.severity !== 'error') {
        setTimeout(() => notification.close(), 5000);
      }
    }
  }, []);

  // Hook para estadísticas de alertas
  const getAlertStatistics = useCallback(() => {
    const total = state.alerts.length;
    const unread = state.unreadCount;
    const byType = state.alerts.reduce((acc, alert) => {
      acc[alert.alert_type] = (acc[alert.alert_type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const bySeverity = state.alerts.reduce((acc, alert) => {
      acc[alert.severity] = (acc[alert.severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const recentCount = getRecentAlerts(24).length;

    return {
      total,
      unread,
      read: total - unread,
      byType,
      bySeverity,
      recent24h: recentCount
    };
  }, [state.alerts, state.unreadCount, getRecentAlerts]);

  // =====================================================
  // RETURN
  // =====================================================

  return {
    // Estado
    data: state,
    isLoading,
    error,
    
    // Operaciones básicas
    loadAlerts,
    loadUnreadAlerts,
    getAlert,
    markAsRead,
    markAllAsRead,
    
    // Utilidades
    refreshAlerts,
    clearError,
    setSelectedAlert,
    
    // Filtros y helpers
    getAlertsByType,
    getAlertsBySeverity,
    getRecentAlerts,
    
    // Control de polling
    startPolling,
    stopPolling,
    isPolling,
    
    // Funciones adicionales
    requestNotificationPermission,
    showBrowserNotification,
    getAlertStatistics
  };
};

// =====================================================
// HOOK COMPLEMENTARIO - useAlertNotifications
// =====================================================

interface UseAlertNotificationsOptions {
  enableBrowserNotifications?: boolean;
  enablePolling?: boolean;
  pollInterval?: number;
}

export const useAlertNotifications = (options: UseAlertNotificationsOptions = {}) => {
  const {
    enableBrowserNotifications = true,
    enablePolling = true,
    pollInterval = 60000
  } = options;

  const alertsHook = useBudgetAlerts({
    autoLoad: true,
    pollInterval,
    onNewAlert: enableBrowserNotifications 
      ? (alert) => alertsHook.showBrowserNotification(alert)
      : undefined
  });

  useEffect(() => {
    if (enableBrowserNotifications) {
      alertsHook.requestNotificationPermission();
    }
  }, [enableBrowserNotifications]);

  useEffect(() => {
    if (enablePolling) {
      alertsHook.startPolling();
      return () => alertsHook.stopPolling();
    }
  }, [enablePolling]);

  return alertsHook;
};

export default useBudgetAlerts;