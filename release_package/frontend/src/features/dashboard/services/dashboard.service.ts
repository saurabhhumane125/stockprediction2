import { dashboardApi } from "@/lib/api/dashboard";
import { mapDashboardResponse } from "../types/dashboard.mapper";
import type { DashboardViewModel } from "../types/dashboard.view.types";

export const dashboardService = {
  async getDashboard(symbol: string): Promise<DashboardViewModel> {
    const dto = await dashboardApi.getDashboard(symbol);
    return mapDashboardResponse(dto);
  },
};