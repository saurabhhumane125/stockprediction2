import { backtestingApi } from "@/lib/api/services";
import { mapBacktesting } from "../types/backtesting.mapper";
import type { BacktestingViewModel } from "../types/backtesting.view.types";

export const backtestingService = {
  async getBacktesting(symbol: string): Promise<BacktestingViewModel> {
    const data = await backtestingApi.getBacktesting(symbol);
    return mapBacktesting(data);
  },
};