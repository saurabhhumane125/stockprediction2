"use client";

import { useCallback, useEffect, useState } from "react";
import { analyticsService, AnalyticsViewModel } from "../services/analytics.service";

export function useAnalytics() {
  const [data, setData] = useState<AnalyticsViewModel | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await analyticsService.getAnalytics();
      setData(result);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || err.message || "Failed to load analytics data."
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