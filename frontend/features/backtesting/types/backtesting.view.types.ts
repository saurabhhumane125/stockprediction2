export interface LatestPredictionViewModel {

  prediction: string;

  confidence: number;

  createdAt: string;

  isCorrect: boolean | null;

}

export interface BacktestingViewModel {

  stock: string;

  totalPredictions: number;

  evaluatedPredictions: number;

  pendingPredictions: number;

  wins: number;

  losses: number;

  accuracy: number;

  winRate: number;

  lossRate: number;

  averageConfidence: number;

  latestPrediction: LatestPredictionViewModel | null;

}