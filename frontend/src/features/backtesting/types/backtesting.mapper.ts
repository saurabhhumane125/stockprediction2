import type {

  BacktestingDto,

} from "./backtesting.types";

import type {

  BacktestingViewModel,

} from "./backtesting.view.types";

export function mapBacktesting(

  dto: BacktestingDto,

): BacktestingViewModel {

  return {

    stock: dto.stock,

    totalPredictions:
      dto.total_predictions,

    evaluatedPredictions:
      dto.evaluated_predictions,

    pendingPredictions:
      dto.pending_predictions,

    wins:
      dto.wins,

    losses:
      dto.losses,

    accuracy:
      dto.accuracy,

    winRate:
      dto.win_rate,

    lossRate:
      dto.loss_rate,

    averageConfidence:
      dto.average_confidence,

    latestPrediction:

      dto.latest_prediction

        ? {

            prediction:
              dto.latest_prediction.prediction,

            confidence:
              dto.latest_prediction.confidence,

            createdAt:
              dto.latest_prediction.created_at,

            isCorrect:
              dto.latest_prediction.is_correct,

          }

        : null,

  };

}