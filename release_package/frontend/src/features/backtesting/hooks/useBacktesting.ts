"use client";

import { useCallback, useEffect, useState } from "react";
import { backtestingService } from "../services/backtesting.service";
import type { BacktestingViewModel } from "../types/backtesting.view.types";

export function useBacktesting(symbol: string) {
  const [data, setData] = useState<BacktestingViewModel | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!symbol) return;
    try {
      setLoading(true);
      setError(null);
      const result = await backtestingService.getBacktesting(symbol);
      setData(result);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || err.message || "Failed to load backtesting data."
      );
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, loading, error, refresh };
}