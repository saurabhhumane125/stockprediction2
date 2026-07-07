import { predictStock } from "../api/prediction.api";

import { mapPredictionResponse } from "../types/prediction.mapper";

export const predictionService = {

  async predict(
    stock: string,
  ) {

    const response =
      await predictStock(stock);

    return mapPredictionResponse(
      response,
    );

  },

};