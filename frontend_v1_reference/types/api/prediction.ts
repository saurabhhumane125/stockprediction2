export interface LatestFeaturesResponse {

  Open: number;
  High: number;
  Low: number;
  Close: number;
  Volume: number;

  RSI: number;
  MACD: number;

  EMA20: number;
  EMA50: number;

  ATR: number;
  ADX: number;

  BB_UPPER: number;
  BB_LOWER: number;
  BB_WIDTH: number;

  ROC: number;
  MOMENTUM: number;

  DAILY_RETURN: number;
  VOLATILITY: number;
  VOLUME_CHANGE: number;

}

export interface LatestCandleResponse {

  date: string;

  open: number;
  high: number;
  low: number;
  close: number;

  volume: number;

}

export interface ExplanationResponse {

  trend: string;

  trend_strength: string;

  rsi: number;

  rsi_state: string;

  roc: number;

  momentum: number;

  volatility: number;

  atr: number;

  bollinger_width: number;

  price_position: string;

  volume_change: number;

  volume_trend: string;

  summary: string[];

}

export interface MarketRegimeResponse {

  regime: string;

  trend: string;

  trend_strength: string;

  volatility: string;

  momentum: string;

}

export interface PredictionResponse {

  prediction: string;

  class_id: number | null;

  confidence: number;

  probability_buy: number | null;

  probability_sell: number | null;

  stock: string;

  sentiment: string | null;

  sentiment_score: number | null;

  technical_signal: string | null;

  news_signal: string | null;

  final_reason: string | null;

  latest_features: LatestFeaturesResponse | null;

  latest_candle: LatestCandleResponse | null;

  explanation: ExplanationResponse | null;

  market_regime: MarketRegimeResponse | null;

}