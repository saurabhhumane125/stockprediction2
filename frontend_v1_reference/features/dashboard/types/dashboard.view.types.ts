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

export interface PredictionViewModel {

  prediction: string;

  confidence: number;

  probabilityBuy: number | null;

  probabilitySell: number | null;

  sentiment: string | null;

  technicalSignal: string | null;

  newsSignal: string | null;

  finalReason: string | null;

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