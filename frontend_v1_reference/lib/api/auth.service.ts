import { apiClient } from "./client";

import type {
  LoginRequest,
  RegisterRequest,
  LoginResponse,
} from "@/features/auth/types/auth.types";

class AuthService {
  async login(
    payload: LoginRequest
  ): Promise<LoginResponse> {
    const { data } = await apiClient.post(
      "/auth/login",
      payload
    );

    return data;
  }

  async register(
    payload: RegisterRequest
  ) {
    const { data } = await apiClient.post(
      "/auth/register",
      payload
    );

    return data;
  }
}

export const authService =
  new AuthService();