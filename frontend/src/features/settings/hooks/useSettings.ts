"use client";

import { useState, useEffect, useCallback } from "react";
import { settingsService } from "../services/settings.service";
import { authApi } from "@/lib/api/auth";
import type { SettingsViewModel } from "../types/settings.types";

export function useSettings() {
  const [data, setData] = useState<SettingsViewModel | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await settingsService.getSettings();
      setData(result);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || err.message || "Failed to load user profile."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch (e) {
      // Ignore logout failure
    } finally {
      localStorage.removeItem("auth_token");
      window.location.href = "/login";
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, loading, error, refresh, logout };
}