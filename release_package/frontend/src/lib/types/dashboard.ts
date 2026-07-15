export interface StockResponse {
  id: number
  symbol: string
  company_name: string
  sector?: string
}

export interface HistoricalPriceResponse {
  id: number
  stock_id: number
  date: string
  open_price: number
  high_price: number
  low_price: number
  close_price: number
  volume: number
  created_at: string
}

export interface RecommendationResponse {
  action: string
  strength: string
  confidence: number
  prediction: string
  sentiment: string
  sentiment_score: number
  class_id?: number
  probability_buy?: number
  probability_sell?: number
  technical_signal: string
  news_signal: string
  reason: string
  summary: string
}

export interface ExplanationResponse {
  trend: string
  trend_strength: string
  rsi: number
  rsi_state: string
  roc: number
  momentum: number
  volatility: number
  atr: number
  bollinger_width: number
  price_position: string
  volume_change: number
  volume_trend: string
  summary: string[]
}

export interface MarketRegimeResponse {
  regime: string
  trend: string
  trend_strength: string
  volatility: string
  momentum: string
}

export interface LatestFeaturesResponse {
  Open: number
  High: number
  Low: number
  Close: number
  Volume: number
  RSI: number
  MACD: number
  EMA20: number
  EMA50: number
  ATR: number
  ADX: number
  BB_UPPER: number
  BB_LOWER: number
  BB_WIDTH: number
  ROC: number
  MOMENTUM: number
  DAILY_RETURN: number
  VOLATILITY: number
  VOLUME_CHANGE: number
}

export interface LatestCandleResponse {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface PredictionResponse {
  prediction: string
  class_id?: number
  confidence: number
  probability_buy?: number
  probability_sell?: number
  stock: string
  sentiment?: string
  sentiment_score?: number
  technical_signal?: string
  news_signal?: string
  final_reason?: string
  latest_features?: LatestFeaturesResponse
  latest_candle?: LatestCandleResponse
  explanation?: ExplanationResponse
  market_regime?: MarketRegimeResponse
}

export interface DashboardResponse {
  stock: StockResponse
  latest_price?: HistoricalPriceResponse
  latest_prediction?: PredictionResponse
  recommendation?: RecommendationResponse
}
