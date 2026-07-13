export interface AnalyticsOverviewViewModel {

  totalPredictions: number;

  pendingPredictions: number;

  completedPredictions: number;

  correctPredictions: number;

  incorrectPredictions: number;

  accuracy: number;

}

export interface DistributionViewModel {

  buy: number;

  sell: number;

}

export interface ConfidenceViewModel {

  average: number;

  minimum: number;

  maximum: number;

}

export interface RecentPredictionViewModel {

  id: number;

  stockId: number;

  prediction: string;

  status: string;

  confidence: number;

  predictionDate: string;

  createdAt: string;

}

export interface AnalyticsViewModel {

  overview: AnalyticsOverviewViewModel;

  distribution: DistributionViewModel;

  confidence: ConfidenceViewModel;

  recent: RecentPredictionViewModel[];

}