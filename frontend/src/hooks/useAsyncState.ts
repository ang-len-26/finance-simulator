import { useState, useCallback } from 'react';

// Hook para manejar estados de carga
export function useAsyncState<T>(
  initialValue: T | null = null
): [
  { data: T | null; loading: boolean; error: string | null },
  {
    setData: (data: T | null) => void;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
    reset: () => void;
  }
] {
  const [data, setData] = useState<T | null>(initialValue);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reset = useCallback(() => {
    setData(initialValue);
    setLoading(false);
    setError(null);
  }, [initialValue]);

  return [
    { data, loading, error },
    { setData, setLoading, setError, reset }
  ];
}