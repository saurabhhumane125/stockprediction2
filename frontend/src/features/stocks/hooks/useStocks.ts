"use client";

import { useCallback, useEffect, useState } from "react";
import { stocksService } from "../services/stocks.service";
import type { StockViewModel } from "../types/stock.view.types";
import { predictionApi } from "@/lib/api/services";

export function useStocks() {
  const [data, setData] = useState<StockViewModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [predictingState, setPredictingState] = useState<Record<string, boolean>>({});

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await stocksService.getStocks();
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "Failed to load stocks.");
    } finally {
      setLoading(false);
    }
  }, []);

  const runPrediction = useCallback(async (symbol: string, onSuccess: () => void) => {
    try {
      setPredictingState((prev) => ({ ...prev, [symbol]: true }));
      await predictionApi.predictLive(symbol);
      onSuccess();
    } catch (err) {
      // Ignoring errors per previous implementation (or handle gracefully)
      alert("Failed to run prediction for " + symbol);
    } finally {
      setPredictingState((prev) => ({ ...prev, [symbol]: false }));
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, loading, error, refresh, predictingState, runPrediction };
}