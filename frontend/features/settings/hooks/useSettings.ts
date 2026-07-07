"use client";

import {

  useCallback,

  useEffect,

  useState,

} from "react";

import { settingsService } from "../services/settings.service";

import type {

  SettingsData,

} from "../types/settings.types";

export function useSettings() {

  const [

    data,

    setData,

  ] = useState<SettingsData | null>(

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

  const refresh = useCallback(

    async () => {

      try {

        setLoading(true);

        setError(null);

        const result =

          await settingsService.getSettings();

        setData(result);

      }

      catch (err) {

        setError(

          err instanceof Error

            ? err.message

            : "Unable to load settings.",

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

      void refresh();

    });

  }, [

    refresh,

  ]);

  return {

    data,

    loading,

    error,

    refresh,

  };

}