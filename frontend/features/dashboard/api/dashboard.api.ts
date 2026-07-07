import { apiRequest } from "@/lib/api";

import type { DashboardResponse } from "@/types/api/dashboard";

export function getDashboard(

  symbol: string,

): Promise<DashboardResponse> {

  return apiRequest<DashboardResponse>(

    `/dashboard/${symbol}`,

  );

}