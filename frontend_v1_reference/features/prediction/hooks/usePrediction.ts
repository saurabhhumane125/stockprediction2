"use client";

import { useState } from "react";

import type { PredictionViewModel } from "../types/prediction.view.types";

import { predictionService } from "../services/prediction.service";

export function usePrediction() {

  const [data, setData] =
    useState<PredictionViewModel | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  async function predict(
    stock: string,
  ) {

    try {

      setLoading(true);

      setError(null);

      const result =
        await predictionService.predict(
          stock,
        );

      setData(result);

    }

    catch (err) {

      setError(

        err instanceof Error

          ? err.message

          : "Prediction failed.",

      );

    }

    finally {

      setLoading(false);

    }

  }

  return {

    data,

    loading,

    error,

    predict,

  };

}