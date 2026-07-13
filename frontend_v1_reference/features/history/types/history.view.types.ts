export interface HistoryItem {

  id: number;

  symbol: string;

  prediction: string;

  confidence: number;

  probabilityBuy: number | null;

  probabilitySell: number | null;

  createdAt: string;

}

export interface HistoryViewModel {

  history: HistoryItem[];

}