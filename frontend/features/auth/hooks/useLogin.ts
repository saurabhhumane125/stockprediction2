"use client";

import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";

import { loginSchema } from "../schemas/login.schema";
import { login } from "../api/auth.api";

import type {
  LoginRequest,
} from "../types/auth.types";

export function useLogin() {

  const router = useRouter();

  const {

    register,

    handleSubmit,

    formState: {

      errors,

      isSubmitting,

    },

  } = useForm<LoginRequest>({

    resolver: zodResolver(loginSchema),

  });

  async function onSubmit(

    values: LoginRequest,

  ) {

    await login(values);

    router.replace("/dashboard");

    router.refresh();

  }

  return {

    register,

    handleSubmit,

    onSubmit,

    errors,

    loading: isSubmitting,

  };

}