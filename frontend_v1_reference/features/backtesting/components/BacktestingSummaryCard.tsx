import { Card, CardContent, CardTitle } from "@/components/ui/Card";
import type { BacktestingViewModel } from "../types/backtesting.view.types";

interface Props {
  data: BacktestingViewModel;
}

export function BacktestingSummaryCard({ data }: Readonly<Props>) {
  const metrics = [
    { label: "Total", value: data.totalPredictions },
    { label: "Evaluated", value: data.evaluatedPredictions },
    { label: "Pending", value: data.pendingPredictions },
    { label: "Wins", value: data.wins },
    { label: "Losses", value: data.losses },
    { label: "Accuracy", value: `${data.accuracy}%` },
  ];

  return (
    <Card padding="none">
      <div className="px-6 py-5 border-b border-[#F0F4F8]">
        <CardTitle>Backtesting Summary</CardTitle>
      </div>

      <CardContent className="p-6">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
          {metrics.map((metric) => (
            <div
              key={metric.label}
              className="rounded-[12px] border border-[#E8EDF2] bg-white p-5 transition-all duration-150 hover:border-[#D7DEE7] hover:shadow-[0_2px_8px_rgba(17,19,26,0.04)]"
            >
              <p className="text-[13px] font-semibold uppercase tracking-[0.08em] text-[#8B95A5]">
                {metric.label}
              </p>
              <h3 className="mt-3 text-3xl font-bold tracking-tight text-[#11131A] font-[family-name:var(--font-space-grotesk)] font-tabular">
                {metric.value}
              </h3>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}