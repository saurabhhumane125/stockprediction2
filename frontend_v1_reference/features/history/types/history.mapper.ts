import type {
  PredictionHistoryDto,
} from "./history.types";

import type {
  HistoryViewModel,
} from "./history.view.types";

export function mapHistory(
  dto: PredictionHistoryDto[],
): HistoryViewModel {

  return {

    history: dto.map((row) => ({

      id: row.id,

      symbol: row.symbol,

      prediction: row.prediction,

      confidence: row.confidence,

      probabilityBuy:
        row.probability_buy,

      probabilitySell:
        row.probability_sell,

      createdAt:
        row.created_at,

    })),

  };

}