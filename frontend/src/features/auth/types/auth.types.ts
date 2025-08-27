// Basado en tus serializers de core/
export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
}

export interface UserProfile {
  username: string;
  email: string;
  is_demo: boolean;
  demo_expires: string | null;
  created_at: string;
  account_count: number;
  transaction_count: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  confirm_password: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

export interface RefreshTokenRequest {
  refresh: string;
}