import { apiRequest } from "./api";

import type {

  LoginRequest,

  LoginResponse,

  RegisterRequest,

} from "@/types/auth";

export function login(

  payload: LoginRequest

) {

  return apiRequest<LoginResponse>(

    "/auth/login",

    {

      method: "POST",

      body: JSON.stringify(payload),

    }

  );

}

export function register(

  payload: RegisterRequest

) {

  return apiRequest(

    "/auth/register",

    {

      method: "POST",

      body: JSON.stringify(payload),

    }

  );

}