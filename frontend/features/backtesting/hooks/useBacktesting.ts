"use client";

import { useCallback, useState } from "react";

import { backtestingService } from "../services/backtesting.service";
import { mapBacktesting } from "../types/backtesting.mapper";

import type {
  BacktestingViewModel,
} from "../types/backtesting.view.types";

export function useBacktesting() {

  const [data, setData] =
    useState<BacktestingViewModel | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const refresh = useCallback(

    async (symbol: string) => {

      try {

        setLoading(true);

        setError("");

        const response =
          await backtestingService.getBacktesting(
            symbol,
          );

        setData(
          mapBacktesting(response),
        );

      }

      catch (err) {

        setError(

          err instanceof Error

            ? err.message

            : "Failed to load backtesting.",

        );

      }

      finally {

        setLoading(false);

      }

    },

    [],

  );

  return {

    data,

    loading,

    error,

    refresh,

  };

}