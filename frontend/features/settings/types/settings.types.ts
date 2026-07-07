export interface SettingsUser {

  id: number;

  full_name: string;

  email: string;

  is_active: number;

}

export interface SettingsData {

  user: SettingsUser;

  apiStatus: string;

  appName: string;

  version: string;

}