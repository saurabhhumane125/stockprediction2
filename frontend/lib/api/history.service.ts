import { apiClient } from "./client";

class HistoryService {

  all() {

    return apiClient.get("/history");

  }

  stock(symbol: string) {

    return apiClient.get(
      `/history/${symbol}`
    );

  }

  latest(symbol: string) {

    return apiClient.get(
      `/history/latest/${symbol}`
    );

  }

}

export const historyService =
  new HistoryService();