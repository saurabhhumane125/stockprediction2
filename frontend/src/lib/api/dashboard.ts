import { api } from "./index"
import type { DashboardResponse } from "../types/dashboard"

export const dashboardApi = {
  getDashboard: async (symbol: string): Promise<DashboardResponse> => {
    const response = await api.get(`/dashboard/${symbol}`)
    return response.data
  },
}
