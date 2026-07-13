export interface PredictionHistoryDto {

  id: number;

  symbol: string;

  prediction: string;

  confidence: number;

  probability_buy: number | null;

  probability_sell: number | null;

  created_at: string;

}