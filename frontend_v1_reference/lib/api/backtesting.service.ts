import { apiClient } from "./client";

class BacktestingService {

  summary(symbol: string) {

    return apiClient.get(
      `/backtesting/${symbol}`
    );

  }

}

export const backtestingService =
  new BacktestingService();