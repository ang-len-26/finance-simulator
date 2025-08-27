import { useState, useCallback } from 'react';

// Hook para manejo de paginación DRF
export function usePagination<T = any>() {
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 50,
    count: 0,
    next: null as string | null,
    previous: null as string | null,
  });

  const updatePagination = useCallback((response: any) => {
    if (response && 'count' in response) {
      setPagination({
        page: 1, // Calcular página actual basado en offset
        page_size: response.results?.length || 50,
        count: response.count,
        next: response.next,
        previous: response.previous,
      });
    }
  }, []);

  const goToPage = useCallback((page: number) => {
    setPagination(prev => ({ ...prev, page }));
  }, []);

  const changePageSize = useCallback((page_size: number) => {
    setPagination(prev => ({ ...prev, page_size, page: 1 }));
  }, []);

  return {
    pagination,
    updatePagination,
    goToPage,
    changePageSize,
    hasNext: !!pagination.next,
    hasPrevious: !!pagination.previous,
  };
}