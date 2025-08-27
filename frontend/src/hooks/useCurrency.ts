import { useCallback } from 'react';
// Hook para formato de moneda
export function useCurrency(locale: string = 'es-PE'): {
  formatCurrency: (amount: number | string, currency?: string) => string;
  parseCurrency: (formatted: string) => number;
} {
  const formatCurrency = useCallback((
	amount: number | string,
	currency: string = 'PEN'
  ): string => {
	const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
	
	if (isNaN(numAmount)) return '0.00';
	
	return new Intl.NumberFormat(locale, {
	  style: 'currency',
	  currency: currency,
	  minimumFractionDigits: 2,
	}).format(numAmount);
  }, [locale]);

  const parseCurrency = useCallback((formatted: string): number => {
	const cleaned = formatted.replace(/[^\d.-]/g, '');
	return parseFloat(cleaned) || 0;
  }, []);

  return { formatCurrency, parseCurrency };
}