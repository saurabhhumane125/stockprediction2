export interface AnalyticsOverview {
  total_predictions: number;
  pending_predictions: number;
  completed_predictions: number;
  correct_predictions: number;
  incorrect_predictions: number;
  accuracy: number;
}

export interface PredictionDistribution {
  BUY: number;
  SELL: number;
}

export interface ConfidenceStatistics {
  average_confidence: number;
  minimum_confidence: number;
  maximum_confidence: number;
}

export interface RecentPrediction {
  id: number;
  stock_id: number;
  prediction: string;
  status: string;
  confidence: number;
  prediction_date: string;
  created_at: string;
}

export interface AnalyticsData {
  overview: AnalyticsOverview;
  distribution: PredictionDistribution;
  confidence: ConfidenceStatistics;
  recent: RecentPrediction[];
}