import { apiClient } from "./client";

class DashboardService {

  async getDashboard(
    symbol: string
  ) {

    const { data } =
      await apiClient.get(
        `/dashboard/${symbol}`
      );

    return data;

  }

}

export const dashboardService =
  new DashboardService();