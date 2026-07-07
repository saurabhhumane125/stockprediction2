export interface LoginRequest {

  email: string;

  password: string;

}

export interface RegisterRequest {

  full_name: string;

  email: string;

  password: string;

}

export interface AuthUser {

  id: number;

  full_name: string;

  email: string;

  is_active?: number;

}

export interface LoginResponse {

  message: string;

  user: AuthUser;

}