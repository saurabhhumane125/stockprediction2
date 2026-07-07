import { apiRequest } from "@/lib/api";

import type { StockResponse } from "@/types/api/stock";

export function getStocks(): Promise<StockResponse[]> {

  return apiRequest<StockResponse[]>(

    "/stocks/",

  );

}