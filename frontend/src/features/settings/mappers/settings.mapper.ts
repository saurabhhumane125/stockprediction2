import type { SettingsUserDTO, SettingsViewModel } from "../types/settings.types";

export const settingsMapper = {
  toViewModel(dto: SettingsUserDTO): SettingsViewModel {
    return {
      user: {
        id: dto.id,
        fullName: dto.full_name,
        email: dto.email,
        isActive: dto.is_active === 1
      }
    };
  }
};
