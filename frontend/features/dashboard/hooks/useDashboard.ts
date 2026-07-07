"use client";

import {

  useCallback,

  useEffect,

  useState,

} from "react";

import { dashboardService } from "../services/dashboard.service";

import type {

  DashboardViewModel,

} from "../types/dashboard.view.types";

export function useDashboard(

  symbol: string,

) {

  const [

    data,

    setData,

  ] = useState<DashboardViewModel | null>(

    null,

  );

  const [

    loading,

    setLoading,

  ] = useState(true);

  const [

    error,

    setError,

  ] = useState<string | null>(

    null,

  );

  const load = useCallback(

    async () => {

      try {

        setLoading(true);

        setError(null);

        const result =

          await dashboardService.getDashboard(

            symbol,

          );

        setData(

          result,

        );

      }

      catch (err) {

        setError(

          err instanceof Error

            ? err.message

            : "Unable to load dashboard.",

        );

      }

      finally {

        setLoading(false);

      }

    },

    [symbol],

  );

  useEffect(() => {

    queueMicrotask(() => {

      void load();

    });

  }, [load]);

  return {

    data,

    loading,

    error,

    refresh: load,

  };

}