import { apiRequest } from "@/lib/api";

import type {
  PredictionHistoryDto,
} from "../types/history.types";

export function getHistory(): Promise<PredictionHistoryDto[]> {

  return apiRequest<PredictionHistoryDto[]>(

    "/history",

  );

}