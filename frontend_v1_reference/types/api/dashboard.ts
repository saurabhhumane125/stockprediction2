import type { HistoricalPriceResponse } from "./historical-price";
import type { PredictionResponse } from "./prediction";
import type { StockResponse } from "./stock";

export interface RecommendationResponse {

  action: string;

  strength: string;

  confidence: number;

  prediction: string;

  sentiment: string;

  sentiment_score: number;

  class_id: number | null;

  probability_buy: number | null;

  probability_sell: number | null;

  technical_signal: string;

  news_signal: string;

  reason: string;

  summary: string;

}

export interface DashboardResponse {

  stock: StockResponse;

  latest_price: HistoricalPriceResponse | null;

  latest_prediction: PredictionResponse | null;

  recommendation: RecommendationResponse | null;

}