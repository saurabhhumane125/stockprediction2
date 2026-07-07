"use client";

import {
  useCallback,
  useState,
} from "react";

import { mapAnalytics } from "../types/analytics.mapper";

import type {

  AnalyticsViewModel,

} from "../types/analytics.view.types";

import { analyticsService } from "../services/analytics.service";

import type {
  AnalyticsData,
} from "../types/analytics.types";

export function useAnalytics() {

  const [data, setData] =
  useState<AnalyticsViewModel | null>(null);
    useState<AnalyticsData | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const refresh = useCallback(async () => {

    try {

      setLoading(true);

      setError(null);

      const [

        overview,

        distribution,

        confidence,

        recent,

      ] = await Promise.all([

        analyticsService.getOverview(),

        analyticsService.getDistribution(),

        analyticsService.getConfidence(),

        analyticsService.getRecent(),

      ]);

        setData(

          mapAnalytics({

           overview,

           distribution,

           confidence,

           recent,

        }),

);

    }

    catch (err) {

      setError(

        err instanceof Error

          ? err.message

          : "Failed to load analytics.",

      );

    }

    finally {

      setLoading(false);

    }

  }, []);

  return {

    data,

    loading,

    error,

    refresh,

  };

}