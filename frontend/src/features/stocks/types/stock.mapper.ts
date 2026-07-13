import type { StockResponse } from "@/lib/types/dashboard";
import type { StockViewModel } from "./stock.view.types";

export function mapStocks(stocks: StockResponse[]): StockViewModel[] {
  return stocks.map((stock) => ({
    id: stock.id,
    symbol: stock.symbol,
    companyName: stock.company_name,
    sector: stock.sector ?? "Equities",
  }));
}