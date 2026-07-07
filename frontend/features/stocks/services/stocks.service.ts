import { getStocks } from "../api/stocks.api";

import type { StockResponse } from "@/types/api/stock";

export const stocksService = {

  async getAll(): Promise<StockResponse[]> {

    return getStocks();

  },

};