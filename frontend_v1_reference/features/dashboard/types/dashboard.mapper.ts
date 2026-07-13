import type { DashboardResponse } from "@/types/api/dashboard";

import type {
  DashboardViewModel,
} from "./dashboard.view.types";

export function mapDashboardResponse(
  dto: DashboardResponse,
): DashboardViewModel {

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
          probabilityBuy:
            dto.latest_prediction.probability_buy,
          probabilitySell:
            dto.latest_prediction.probability_sell,
          sentiment:
            dto.latest_prediction.sentiment,
          technicalSignal:
            dto.latest_prediction.technical_signal,
          newsSignal:
            dto.latest_prediction.news_signal,
          finalReason:
            dto.latest_prediction.final_reason,
        }
      : null,

    recommendation: dto.recommendation
      ? {
          action: dto.recommendation.action,
          strength: dto.recommendation.strength,
          confidence: dto.recommendation.confidence,
          prediction: dto.recommendation.prediction,
          sentiment: dto.recommendation.sentiment,
          sentimentScore:
            dto.recommendation.sentiment_score,
          probabilityBuy:
            dto.recommendation.probability_buy,
          probabilitySell:
            dto.recommendation.probability_sell,
          technicalSignal:
            dto.recommendation.technical_signal,
          newsSignal:
            dto.recommendation.news_signal,
          reason:
            dto.recommendation.reason,
          summary:
            dto.recommendation.summary,
        }
      : null,

  };

}