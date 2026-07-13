import { stocksApi } from "@/lib/api/services";
import { mapStocks } from "../types/stock.mapper";
import type { StockViewModel } from "../types/stock.view.types";

export const stocksService = {
  async getStocks(): Promise<StockViewModel[]> {
    const data = await stocksApi.getStocks();
    return mapStocks(data);
  },
};