import { getDashboard } from "../api/dashboard.api";

import { mapDashboardResponse } from "../types/dashboard.mapper";

import type { DashboardViewModel } from "../types/dashboard.view.types";

export const dashboardService = {

  async getDashboard(

    symbol: string,

  ): Promise<DashboardViewModel> {

    const response = await getDashboard(

      symbol,

    );

    return mapDashboardResponse(

      response,

    );

  },

};