import type { DashboardResponse } from "@/lib/types/dashboard";
import type { DashboardViewModel } from "./dashboard.view.types";

export function mapDashboardResponse(dto: DashboardResponse): DashboardViewModel {
  return {
    stock: {
      symbol: dto.stock.symbol,
      companyName: dto.stock.company_name,
      sector: dto.stock.sector ?? "N/A",
    },
    latestPrice: dto.latest_price
      ? {
          price: dto.latest_price.close_price,
          open: dto.latest_price.open_price,
          high: dto.latest_price.high_price,
          low: dto.latest_price.low_price,
          volume: dto.latest_price.volume,
          date: dto.latest_price.date,
        }
      : null,
    prediction: dto.latest_prediction
      ? {
          prediction: dto.latest_prediction.prediction,
          confidence: dto.latest_prediction.confidence,
          probabilityBuy: dto.latest_prediction.probability_buy ?? 0,
          probabilitySell: dto.latest_prediction.probability_sell ?? 0,
          sentiment: dto.latest_prediction.sentiment ?? "NEUTRAL",
          technicalSignal: dto.latest_prediction.technical_signal ?? "Neutral",
          newsSignal: dto.latest_prediction.news_signal ?? "Neutral",
          finalReason: dto.latest_prediction.final_reason ?? "No reason provided",
          explanation: dto.latest_prediction.explanation 
            ? {
                trend: dto.latest_prediction.explanation.trend,
                trendStrength: dto.latest_prediction.explanation.trend_strength,
                rsi: dto.latest_prediction.explanation.rsi,
                rsiState: dto.latest_prediction.explanation.rsi_state,
                roc: dto.latest_prediction.explanation.roc,
                momentum: dto.latest_prediction.explanation.momentum,
                volatility: dto.latest_prediction.explanation.volatility,
                atr: dto.latest_prediction.explanation.atr,
                bollingerWidth: dto.latest_prediction.explanation.bollinger_width,
                pricePosition: dto.latest_prediction.explanation.price_position,
                volumeChange: dto.latest_prediction.explanation.volume_change,
                volumeTrend: dto.latest_prediction.explanation.volume_trend,
                summary: dto.latest_prediction.explanation.summary,
              }
            : null,
          marketRegime: dto.latest_prediction.market_regime
            ? {
                regime: dto.latest_prediction.market_regime.regime,
                trend: dto.latest_prediction.market_regime.trend,
                trendStrength: dto.latest_prediction.market_regime.trend_strength,
                volatility: dto.latest_prediction.market_regime.volatility,
                momentum: dto.latest_prediction.market_regime.momentum,
              }
            : null,
          latestCandle: dto.latest_prediction.latest_candle
            ? {
                date: dto.latest_prediction.latest_candle.date,
                open: dto.latest_prediction.latest_candle.open,
                high: dto.latest_prediction.latest_candle.high,
                low: dto.latest_prediction.latest_candle.low,
                close: dto.latest_prediction.latest_candle.close,
                volume: dto.latest_prediction.latest_candle.volume,
              }
            : null,
        }
      : null,
    recommendation: dto.recommendation
      ? {
          action: dto.recommendation.action,
          strength: dto.recommendation.strength,
          confidence: dto.recommendation.confidence,
          prediction: dto.recommendation.prediction,
          sentiment: dto.recommendation.sentiment,
          sentimentScore: dto.recommendation.sentiment_score,
          probabilityBuy: dto.recommendation.probability_buy ?? 0,
          probabilitySell: dto.recommendation.probability_sell ?? 0,
          technicalSignal: dto.recommendation.technical_signal,
          newsSignal: dto.recommendation.news_signal,
          reason: dto.recommendation.reason,
          summary: dto.recommendation.summary,
        }
      : null,
  };
}