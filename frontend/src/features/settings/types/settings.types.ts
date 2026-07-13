export interface SettingsUserDTO {
  id: number;
  full_name: string;
  email: string;
  is_active: number;
}

export interface SettingsUserViewModel {
  id: number;
  fullName: string;
  email: string;
  isActive: boolean;
}

export interface SettingsViewModel {
  user: SettingsUserViewModel;
}