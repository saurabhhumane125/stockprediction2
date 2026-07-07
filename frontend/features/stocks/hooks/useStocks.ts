"use client";

import {

  useCallback,

  useEffect,

  useState,

} from "react";

import type { StockResponse } from "@/types/api/stock";

import { stocksService } from "../services/stocks.service";

export function useStocks() {

  const [

    stocks,

    setStocks,

  ] = useState<StockResponse[]>([]);

  const [

    loading,

    setLoading,

  ] = useState(true);

  const [

    error,

    setError,

  ] = useState<string | null>(null);

  const load = useCallback(

    async () => {

      try {

        setLoading(true);

        setError(null);

        const result =

          await stocksService.getAll();

        setStocks(result);

      }

      catch (err) {

        setError(

          err instanceof Error

            ? err.message

            : "Unable to load stocks.",

        );

      }

      finally {

        setLoading(false);

      }

    },

    [],

  );

  useEffect(() => {

    queueMicrotask(() => {

      void load();

    });

  }, [load]);

  return {

    stocks,

    loading,

    error,

    refresh: load,

  };

}