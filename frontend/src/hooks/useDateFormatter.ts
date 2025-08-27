import { useState, useEffect, useCallback, useRef } from 'react';

// Hook para formatear fechas
export function useDateFormatter(locale: string = 'es-PE'): {
  formatDate: (date: string | Date, format?: 'short' | 'medium' | 'long') => string;
  formatRelative: (date: string | Date) => string;
  isToday: (date: string | Date) => boolean;
} {
  const formatDate = useCallback((
    date: string | Date,
    format: 'short' | 'medium' | 'long' = 'medium'
  ): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    const options: Intl.DateTimeFormatOptions = {
      short: { day: '2-digit', month: '2-digit', year: 'numeric' },
      medium: { day: '2-digit', month: 'short', year: 'numeric' },
      long: { 
        weekday: 'long', 
        day: '2-digit', 
        month: 'long', 
        year: 'numeric' 
      }
    }[format];

    return new Intl.DateTimeFormat(locale, options).format(dateObj);
  }, [locale]);

  const formatRelative = useCallback((date: string | Date): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const now = new Date();
    const diffInDays = Math.floor((now.getTime() - dateObj.getTime()) / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) return 'Hoy';
    if (diffInDays === 1) return 'Ayer';
    if (diffInDays < 7) return `Hace ${diffInDays} días`;
    if (diffInDays < 30) return `Hace ${Math.floor(diffInDays / 7)} semanas`;
    if (diffInDays < 365) return `Hace ${Math.floor(diffInDays / 30)} meses`;
    
    return `Hace ${Math.floor(diffInDays / 365)} años`;
  }, []);

  const isToday = useCallback((date: string | Date): boolean => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const today = new Date();
    
    return dateObj.toDateString() === today.toDateString();
  }, []);

  return { formatDate, formatRelative, isToday };
}

export * from './useApi';