import { authApi } from "@/lib/api/auth";
import { settingsMapper } from "../mappers/settings.mapper";
import type { SettingsViewModel, SettingsUserDTO } from "../types/settings.types";

export const settingsService = {
  async getSettings(): Promise<SettingsViewModel> {
    const data: SettingsUserDTO = await authApi.me();
    return settingsMapper.toViewModel(data);
  }
};