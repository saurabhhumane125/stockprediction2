export interface HistoricalPriceResponse {

  id: number;

  stock_id: number;

  date: string;

  open_price: number;

  high_price: number;

  low_price: number;

  close_price: number;

  volume: number;

  created_at: string;

}