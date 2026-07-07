import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";

import type {
  BacktestingViewModel,
} from "../types/backtesting.view.types";

interface Props {

  data: BacktestingViewModel;

}

export function PerformanceCard({

  data,

}: Readonly<Props>) {

  return (

    <Card>

      <CardHeader>

        <CardTitle>

          Performance

        </CardTitle>

      </CardHeader>

      <CardContent className="space-y-4">

        <div className="flex justify-between">

          <span>Win Rate</span>

          <strong>

            {data.winRate.toFixed(2)}%

          </strong>

        </div>

        <div className="flex justify-between">

          <span>Loss Rate</span>

          <strong>

            {data.lossRate.toFixed(2)}%

          </strong>

        </div>

        <div className="flex justify-between">

          <span>Average Confidence</span>

          <strong>

            {(data.averageConfidence * 100).toFixed(2)}%

          </strong>

        </div>

      </CardContent>

    </Card>

  );

}