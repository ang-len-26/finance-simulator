import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiError } from '@/types/api.types';

// Token management con nombres consistentes
export const getAccessToken = (): string | null => {
  return localStorage.getItem('fintrack_access_token');
};

export const getRefreshToken = (): string | null => {
  return localStorage.getItem('fintrack_refresh_token');
};

export const setTokens = (access: string, refresh: string): void => {
  localStorage.setItem('fintrack_access_token', access);
  localStorage.setItem('fintrack_refresh_token', refresh);
};

export const clearTokens = (): void => {
  localStorage.removeItem('fintrack_access_token');
  localStorage.removeItem('fintrack_refresh_token');
};

export const isAuthenticated = (): boolean => {
  return !!getAccessToken();
};

class ApiClient {
  private axiosInstance: AxiosInstance;
  private isRefreshing = false;
  private refreshSubscribers: ((token: string) => void)[] = [];
  private baseURL: string;

  constructor() {
    // Configuración mejorada para Vite
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

    this.axiosInstance = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: import.meta.env.VITE_API_TIMEOUT || 10000,
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor para agregar JWT token
    this.axiosInstance.interceptors.request.use(
      (config) => {
        const token = getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        // Log para desarrollo
        if (import.meta.env.DEV) {
          console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        }
        
        return config;
      },
      (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor para manejar refresh token
    this.axiosInstance.interceptors.response.use(
      (response) => {
        // Log para desarrollo
        if (import.meta.env.DEV) {
          console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`);
        }
        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            return new Promise((resolve) => {
              this.refreshSubscribers.push((token: string) => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                resolve(this.axiosInstance.request(originalRequest));
              });
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const refreshToken = getRefreshToken();
            if (!refreshToken) {
              throw new Error('No refresh token available');
            }

            const response = await axios.post(`${this.baseURL}/token/refresh/`, {
              refresh: refreshToken,
            });

            const { access } = response.data;
            setTokens(access, refreshToken);

            this.refreshSubscribers.forEach((callback) => callback(access));
            this.refreshSubscribers = [];

            originalRequest.headers.Authorization = `Bearer ${access}`;
            return this.axiosInstance.request(originalRequest);
          } catch (refreshError) {
            console.error('❌ Token refresh failed:', refreshError);
            clearTokens();
            // Redireccionar a login
            window.location.href = '/auth/login';
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        return Promise.reject(this.handleError(error));
      }
    );
  }

  private handleError(error: any): ApiError {
    console.error('❌ API Error:', error);

    if (error.response) {
      // Error del servidor
      const data = error.response.data;
      return {
        message: data?.detail || data?.message || 'Error del servidor',
        errors: data?.errors || {},
        status: error.response.status,
      };
    } else if (error.request) {
      // Error de red
      return {
        message: 'Error de conexión. Verifica tu conexión a internet.',
        status: 0,
      };
    } else {
      // Error de configuración
      return {
        message: error.message || 'Error inesperado',
        status: 0,
      };
    }
  }

  // Métodos HTTP genéricos
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.axiosInstance.get(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.axiosInstance.post(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.axiosInstance.put(url, data, config);
    return response.data;
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.axiosInstance.patch(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.axiosInstance.delete(url, config);
    return response.data;
  }

  // Método auxiliar para obtener información del cliente
  getBaseURL(): string {
    return this.baseURL;
  }
}

// Exportar instancia singleton
const apiClient = new ApiClient();
export default apiClient;