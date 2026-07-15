export interface StockOverviewViewModel {

  symbol: string;

  companyName: string;

  sector: string;

}

export interface LatestPriceViewModel {

  price: number;

  open: number;

  high: number;

  low: number;

  volume: number;

  date: string;

}

export interface ExplanationViewModel {
  trend: string;
  trendStrength: string;
  rsi: number;
  rsiState: string;
  roc: number;
  momentum: number;
  volatility: number;
  atr: number;
  bollingerWidth: number;
  pricePosition: string;
  volumeChange: number;
  volumeTrend: string;
  summary: string[];
}

export interface MarketRegimeViewModel {
  regime: string;
  trend: string;
  trendStrength: string;
  volatility: string;
  momentum: string;
}

export interface LatestCandleViewModel {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PredictionViewModel {

  prediction: string;

  confidence: number;

  probabilityBuy: number | null;

  probabilitySell: number | null;

  sentiment: string | null;

  technicalSignal: string | null;

  newsSignal: string | null;

  finalReason: string | null;

  explanation: ExplanationViewModel | null;

  marketRegime: MarketRegimeViewModel | null;

  latestCandle: LatestCandleViewModel | null;

}

export interface RecommendationViewModel {

  action: string;

  strength: string;

  confidence: number;

  prediction: string;

  sentiment: string;

  sentimentScore: number;

  probabilityBuy: number | null;

  probabilitySell: number | null;

  technicalSignal: string;

  newsSignal: string;

  reason: string;

  summary: string;

}

export interface DashboardViewModel {

  stock: StockOverviewViewModel;

  latestPrice: LatestPriceViewModel | null;

  prediction: PredictionViewModel | null;

  recommendation: RecommendationViewModel | null;

}