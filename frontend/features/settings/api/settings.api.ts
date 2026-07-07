import { apiRequest } from "@/lib/api";

import type {

  SettingsUser,

} from "../types/settings.types";

export function getCurrentUser() {

  return apiRequest<SettingsUser>(

    "/auth/me",

  );

}