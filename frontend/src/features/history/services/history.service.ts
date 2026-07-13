import { historyApi } from "@/lib/api/services";
import { mapHistory } from "../types/history.mapper";
import type { HistoryViewModel } from "../types/history.view.types";

export const historyService = {
  async getHistory(): Promise<HistoryViewModel> {
    const data = await historyApi.getHistory();
    return mapHistory(data);
  },
};