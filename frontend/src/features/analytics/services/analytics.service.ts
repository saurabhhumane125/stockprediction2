import { analyticsApi } from "@/lib/api/services";

export interface AnalyticsViewModel {
  overview: any;
  distribution: any;
  confidence: any;
}

export const analyticsService = {
  async getAnalytics(): Promise<AnalyticsViewModel> {
    const [overview, distribution, confidence] = await Promise.all([
      analyticsApi.getOverview(),
      analyticsApi.getDistribution(),
      analyticsApi.getConfidence(),
    ]);
    
    return {
      overview: {
        totalPredictions: overview.total_predictions,
        evaluatedPredictions: overview.completed_predictions,
        overallAccuracy: overview.accuracy ? overview.accuracy / 100 : 0,
      },
      distribution: distribution.distribution || {},
      confidence: confidence.confidence_trend || [],
    };
  }
};