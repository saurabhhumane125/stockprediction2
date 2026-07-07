import { apiRequest } from "@/lib/api";

import type { PredictionResponse } from "@/types/api/prediction";

export function predictStock(
  stock: string,
): Promise<PredictionResponse> {

  return apiRequest<PredictionResponse>(
    `/predict/live/${stock}`,
    {
      method: "POST",
    },
  );

}