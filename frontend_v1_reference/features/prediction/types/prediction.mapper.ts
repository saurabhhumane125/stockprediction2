import type { PredictionResponse } from "@/types/api/prediction";

import type { PredictionViewModel } from "./prediction.view.types";

export function mapPredictionResponse(
  dto: PredictionResponse,
): PredictionViewModel {

  return {

    prediction: dto.prediction,

    confidence: dto.confidence,

    probabilityBuy: dto.probability_buy,

    probabilitySell: dto.probability_sell,

    sentiment: dto.sentiment,

    sentimentScore: dto.sentiment_score,

    technicalSignal: dto.technical_signal,

    newsSignal: dto.news_signal,

    finalReason: dto.final_reason,

    stock: dto.stock,

    latestFeatures: dto.latest_features,

    latestCandle: dto.latest_candle,

    explanation: dto.explanation
      ? {
          trend: dto.explanation.trend,
          trendStrength: dto.explanation.trend_strength,
          rsi: dto.explanation.rsi,
          rsiState: dto.explanation.rsi_state,
          roc: dto.explanation.roc,
          momentum: dto.explanation.momentum,
          volatility: dto.explanation.volatility,
          atr: dto.explanation.atr,
          bollingerWidth: dto.explanation.bollinger_width,
          pricePosition: dto.explanation.price_position,
          volumeChange: dto.explanation.volume_change,
          volumeTrend: dto.explanation.volume_trend,
          summary: dto.explanation.summary,
        }
      : null,

    marketRegime: dto.market_regime
      ? {
          regime: dto.market_regime.regime,
          trend: dto.market_regime.trend,
          trendStrength: dto.market_regime.trend_strength,
          volatility: dto.market_regime.volatility,
          momentum: dto.market_regime.momentum,
        }
      : null,

  };

}