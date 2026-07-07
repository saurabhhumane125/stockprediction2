import { apiRequest } from "@/lib/api";

import type {

  BacktestingDto,

} from "../types/backtesting.types";

export function getBacktesting(

  symbol: string,

) {

  return apiRequest<BacktestingDto>(

    `/backtesting/${symbol}`,

  );

}