import type { LatestFeaturesResponse } from "@/types/api/prediction";
export interface PredictionViewModel {

  prediction: string;

  confidence: number;

  probabilityBuy: number | null;

  probabilitySell: number | null;

  sentiment: string | null;

  sentimentScore: number | null;

  technicalSignal: string | null;

  newsSignal: string | null;

  finalReason: string | null;

  stock: string;

  latestFeatures: LatestFeaturesResponse | null;

  latestCandle: {

    date: string;

    open: number;

    high: number;

    low: number;

    close: number;

    volume: number;

  } | null;

  explanation: {

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

  } | null;

  marketRegime: {

    regime: string;

    trend: string;

    trendStrength: string;

    volatility: string;

    momentum: string;

  } | null;

}