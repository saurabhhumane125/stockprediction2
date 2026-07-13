"use client";

import { useCallback, useEffect, useState } from "react";
import { historyService } from "../services/history.service";
import type { HistoryViewModel } from "../types/history.view.types";

export function useHistory() {
  const [data, setData] = useState<HistoryViewModel | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await historyService.getHistory();
      setData(result);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || err.message || "Failed to load history."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, loading, error, refresh };
}