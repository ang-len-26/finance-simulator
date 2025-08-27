import { useState, useCallback } from 'react';
import { ApiError } from '@/types/api.types';
import apiClient from '@/services/api/client';

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  status: LoadingState;
}

export interface UseApiReturn<T> extends UseApiState<T> {
  execute: (...args: any[]) => Promise<T>;
  reset: () => void;
  setData: (data: T | null) => void;
}

export function useApi<T = any>(
  apiFunction: (...args: any[]) => Promise<T>,
  options?: {
    immediate?: boolean;
    initialData?: T;
    onSuccess?: (data: T) => void;
    onError?: (error: ApiError) => void;
    transform?: (data: any) => T; // Nueva opción para transformar datos
  }
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: options?.initialData || null,
    loading: false,
    error: null,
    status: 'idle',
  });

  const execute = useCallback(
    async (...args: any[]): Promise<T> => {
      setState(prev => ({
        ...prev,
        loading: true,
        error: null,
        status: 'loading',
      }));

      try {
        const result = await apiFunction(...args);
        
        // Aplicar transformación si existe
        const transformedResult = options?.transform ? options.transform(result) : result;
        
        setState(prev => ({
          ...prev,
          data: transformedResult,
          loading: false,
          error: null,
          status: 'success',
        }));

        options?.onSuccess?.(transformedResult);
        return transformedResult;
      } catch (error) {
        // Mejorar manejo de errores DRF
        let apiError: ApiError;
        
        if (error && typeof error === 'object' && 'response' in error) {
          const axiosError = error as any;
          const data = axiosError.response?.data;
          
          apiError = {
            message: data?.detail || data?.message || 'Error del servidor',
            errors: data?.errors || (data?.non_field_errors ? { non_field_errors: data.non_field_errors } : {}),
            status: axiosError.response?.status,
            detail: data?.detail,
          };
        } else if (error instanceof Error) {
          apiError = {
            message: error.message,
            status: 0,
          };
        } else {
          apiError = error as ApiError;
        }
        
        setState(prev => ({
          ...prev,
          loading: false,
          error: apiError,
          status: 'error',
        }));

        options?.onError?.(apiError);
        throw apiError;
      }
    },
    [apiFunction, options]
  );

  const reset = useCallback(() => {
    setState({
      data: options?.initialData || null,
      loading: false,
      error: null,
      status: 'idle',
    });
  }, [options?.initialData]);

  const setData = useCallback((data: T | null) => {
    setState(prev => ({
      ...prev,
      data,
    }));
  }, []);

  return {
    ...state,
    execute,
    reset,
    setData,
  };
}

// Hook específico para operaciones CRUD con paginación DRF
export function useCRUD<T = any>(baseUrl: string) {
  const [listState, setListState] = useState<UseApiState<T[]>>({
    data: null,
    loading: false,
    error: null,
    status: 'idle',
  });

  const [itemState, setItemState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
    status: 'idle',
  });

  // Función para manejar respuestas paginadas de DRF
  const handlePaginatedResponse = (response: any): T[] => {
    if (response && 'results' in response) {
      return response.results; // Respuesta paginada DRF
    }
    return response; // Array directo
  };

  const list = useCallback(async (params?: any): Promise<T[]> => {
    setListState(prev => ({ ...prev, loading: true, error: null, status: 'loading' }));
    
    try {
      const result = await apiClient.get<any>(baseUrl, { params });
      const data = handlePaginatedResponse(result);
      
      setListState(prev => ({
        ...prev,
        data,
        loading: false,
        error: null,
        status: 'success',
      }));
      return data;
    } catch (error) {
      const apiError = error as ApiError;
      setListState(prev => ({
        ...prev,
        loading: false,
        error: apiError,
        status: 'error',
      }));
      throw error;
    }
  }, [baseUrl]);

  const get = useCallback(async (id: string | number): Promise<T> => {
    setItemState(prev => ({ ...prev, loading: true, error: null, status: 'loading' }));
    
    try {
      const result = await apiClient.get<T>(`${baseUrl}${id}/`);
      setItemState(prev => ({
        ...prev,
        data: result,
        loading: false,
        error: null,
        status: 'success',
      }));
      return result;
    } catch (error) {
      const apiError = error as ApiError;
      setItemState(prev => ({
        ...prev,
        loading: false,
        error: apiError,
        status: 'error',
      }));
      throw error;
    }
  }, [baseUrl]);

  const create = useCallback(async (data: Partial<T>): Promise<T> => {
    setItemState(prev => ({ ...prev, loading: true, error: null, status: 'loading' }));
    
    try {
      const result = await apiClient.post<T>(baseUrl, data);
      setItemState(prev => ({
        ...prev,
        data: result,
        loading: false,
        error: null,
        status: 'success',
      }));
      
      // Actualizar lista si existe
      if (listState.data) {
        setListState(prev => ({
          ...prev,
          data: [...(prev.data || []), result],
        }));
      }
      
      return result;
    } catch (error) {
      const apiError = error as ApiError;
      setItemState(prev => ({
        ...prev,
        loading: false,
        error: apiError,
        status: 'error',
      }));
      throw error;
    }
  }, [baseUrl, listState.data]);

  const update = useCallback(async (id: string | number, data: Partial<T>): Promise<T> => {
    setItemState(prev => ({ ...prev, loading: true, error: null, status: 'loading' }));
    
    try {
      const result = await apiClient.patch<T>(`${baseUrl}${id}/`, data);
      setItemState(prev => ({
        ...prev,
        data: result,
        loading: false,
        error: null,
        status: 'success',
      }));
      
      // Actualizar lista si existe
      if (listState.data) {
        setListState(prev => ({
          ...prev,
          data: prev.data!.map(item => 
            (item as any).id === id ? result : item
          ),
        }));
      }
      
      return result;
    } catch (error) {
      const apiError = error as ApiError;
      setItemState(prev => ({
        ...prev,
        loading: false,
        error: apiError,
        status: 'error',
      }));
      throw error;
    }
  }, [baseUrl, listState.data]);

  const remove = useCallback(async (id: string | number): Promise<void> => {
    setItemState(prev => ({ ...prev, loading: true, error: null, status: 'loading' }));
    
    try {
      await apiClient.delete(`${baseUrl}${id}/`);
      setItemState(prev => ({
        ...prev,
        data: null,
        loading: false,
        error: null,
        status: 'success',
      }));
      
      // Actualizar lista si existe
      if (listState.data) {
        setListState(prev => ({
          ...prev,
          data: prev.data!.filter(item => (item as any).id !== id),
        }));
      }
    } catch (error) {
      const apiError = error as ApiError;
      setItemState(prev => ({
        ...prev,
        loading: false,
        error: apiError,
        status: 'error',
      }));
      throw error;
    }
  }, [baseUrl, listState.data]);

  return {
    list: {
      ...listState,
      execute: list,
    },
    item: {
      ...itemState,
      execute: get,
    },
    create,
    update,
    remove,
  };
}
