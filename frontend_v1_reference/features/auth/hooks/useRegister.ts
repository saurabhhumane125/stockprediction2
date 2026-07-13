"use client";

import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";

import { register as registerApi } from "../api/auth.api";
import { registerSchema } from "../schemas/register.schema";

import type {
  RegisterRequest,
} from "../types/auth.types";

export function useRegister() {

  const router = useRouter();

  const {

    register,

    handleSubmit,

    formState: {

      errors,

      isSubmitting,

    },

  } = useForm<RegisterRequest>({

    resolver: zodResolver(registerSchema),

  });

  async function onSubmit(

    values: RegisterRequest,

  ) {

    await registerApi(values);

    router.replace("/login");

  }

  return {

    register,

    handleSubmit,

    onSubmit,

    errors,

    loading: isSubmitting,

  };

}