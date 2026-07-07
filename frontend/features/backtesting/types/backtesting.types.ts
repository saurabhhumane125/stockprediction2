export interface LatestPredictionDto {

  prediction: string;

  confidence: number;

  created_at: string;

  is_correct: boolean | null;

}

export interface BacktestingDto {

  stock: string;

  total_predictions: number;

  evaluated_predictions: number;

  pending_predictions: number;

  wins: number;

  losses: number;

  accuracy: number;

  win_rate: number;

  loss_rate: number;

  average_confidence: number;

  latest_prediction: LatestPredictionDto | null;

}