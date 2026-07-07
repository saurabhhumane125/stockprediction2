import { apiClient } from "./client";

class PredictionService {

  async livePrediction(
    stock: string
  ) {

    const { data } =
      await apiClient.post(
        `/predict/live/${stock}`
      );

    return data;

  }

}

export const predictionService =
  new PredictionService();