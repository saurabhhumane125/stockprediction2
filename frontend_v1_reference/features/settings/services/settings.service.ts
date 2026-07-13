import { getCurrentUser } from "../api/settings.api";

import type {

  SettingsData,

} from "../types/settings.types";

export const settingsService = {

  async getSettings():

  Promise<SettingsData> {

    const user =

      await getCurrentUser();

    return {

      user,

      apiStatus: "Connected",

      appName:

        "Stock Price Trend Prediction",

      version: "1.0.0",

    };

  },

};