import {
  login,
  logout,
  me,
  register,
} from "../api/auth.api";

import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  AuthUser,
} from "../types/auth.types";

class AuthService {

  async login(
    payload: LoginRequest,
  ): Promise<LoginResponse> {

    return login(payload);

  }

  async register(
    payload: RegisterRequest,
  ) {

    return register(payload);

  }

  async logout(): Promise<void> {

    await logout();

  }

  async currentUser(): Promise<AuthUser> {

    return me();

  }

}

export const authService = new AuthService();