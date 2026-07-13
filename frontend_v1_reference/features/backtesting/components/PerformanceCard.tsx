import {
  Card,
  CardContent,
  CardLabel,
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
  const metrics = [
    { label: "Win Rate", value: `${data.winRate.toFixed(2)}%` },
    { label: "Loss Rate", value: `${data.lossRate.toFixed(2)}%` },
    { label: "Avg Confidence", value: `${(data.averageConfidence * 100).toFixed(2)}%` },
  ];

  return (
    <Card className="h-full">
      <CardContent className="space-y-6">
        <CardLabel>Performance</CardLabel>

        <div className="space-y-4">
          {metrics.map((m) => (
            <div key={m.label} className="flex items-center justify-between py-2 border-b border-[#F0F4F8] last:border-0">
              <span className="text-[15px] text-[#5B6473] font-medium">{m.label}</span>
              <span className="text-base font-bold text-[#11131A] font-tabular">{m.value}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}