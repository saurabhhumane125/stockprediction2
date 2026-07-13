import { apiClient } from "./client";

class StockService {

  all() {

    return apiClient.get("/stocks");

  }

  bySymbol(symbol: string) {

    return apiClient.get(
      `/stocks/${symbol}`
    );

  }

}

export const stockService =
  new StockService();