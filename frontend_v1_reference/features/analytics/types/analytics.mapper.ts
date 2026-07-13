import type {

  AnalyticsData,

} from "./analytics.types";

import type {

  AnalyticsViewModel,

} from "./analytics.view.types";

export function mapAnalytics(

  dto: AnalyticsData,

): AnalyticsViewModel {

  return {

    overview: {

      totalPredictions:

        dto.overview.total_predictions,

      pendingPredictions:

        dto.overview.pending_predictions,

      completedPredictions:

        dto.overview.completed_predictions,

      correctPredictions:

        dto.overview.correct_predictions,

      incorrectPredictions:

        dto.overview.incorrect_predictions,

      accuracy:

        dto.overview.accuracy,

    },

    distribution: {

      buy:

        dto.distribution.BUY,

      sell:

        dto.distribution.SELL,

    },

    confidence: {

      average:

        dto.confidence.average_confidence,

      minimum:

        dto.confidence.minimum_confidence,

      maximum:

        dto.confidence.maximum_confidence,

    },

    recent:

      dto.recent.map(

        (prediction) => ({

          id: prediction.id,

          stockId: prediction.stock_id,

          prediction:

            prediction.prediction,

          status:

            prediction.status,

          confidence:

            prediction.confidence,

          predictionDate:

            prediction.prediction_date,

          createdAt:

            prediction.created_at,

        }),

      ),

  };

}