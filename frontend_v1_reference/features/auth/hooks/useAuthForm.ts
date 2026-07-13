"use client";

import { useState } from "react";

export function useAuthForm() {

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  async function execute<T>(
    callback: () => Promise<T>,
  ): Promise<T> {

    try {

      setLoading(true);

      setError("");

      return await callback();

    }

    catch (err) {

      const message =

        err instanceof Error

          ? err.message

          : "Something went wrong.";

      setError(message);

      throw err;

    }

    finally {

      setLoading(false);

    }

  }

  return {

    loading,

    error,

    execute,

    clearError: () => setError(""),

  };

}