"use client";

import { useCallback, useState } from "react";

import { historyService } from "../services/history.service";
import { mapHistory } from "../types/history.mapper";

import type { HistoryViewModel } from "../types/history.view.types";

export function useHistory() {

  const [data, setData] =
    useState<HistoryViewModel | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const refresh = useCallback(
    async () => {

      try {

        setLoading(true);

        setError("");

        const response =
          await historyService.getHistory();

        setData(
          mapHistory(response),
        );

      }

      catch (err) {

        setError(

          err instanceof Error

            ? err.message

            : "Failed to load history.",

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