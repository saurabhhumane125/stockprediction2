import { apiClient } from "@/lib/api/client";

import type {

  LoginRequest,

  LoginResponse,

  RegisterRequest,

} from "../types/auth.types";

export async function login(

  payload: LoginRequest,

): Promise<LoginResponse> {

  const { data } = await apiClient.post(

    "/auth/login",

    payload,

  );

  return data;

}

export async function register(

  payload: RegisterRequest,

) {

  const { data } = await apiClient.post(

    "/auth/register",

    payload,

  );

  return data;

}

export async function logout() {

  await apiClient.post(

    "/auth/logout",

  );

}

export async function me() {

  const { data } = await apiClient.get(

    "/auth/me",

  );

  return data;

}