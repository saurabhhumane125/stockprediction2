import {
  Card,
  CardContent,
  CardDescription,
  CardTitle,
} from "@/components/ui/Card";

import type { AnalyticsOverviewViewModel } from "../types/analytics.view.types";

interface AnalyticsOverviewCardProps {
  overview: AnalyticsOverviewViewModel;
}

interface MetricItemProps {
  label: string;
  value: number | string;
  accent?: boolean;
}

function MetricItem({ label, value, accent }: Readonly<MetricItemProps>) {
  return (
    <div className="rounded-[12px] border border-[#E8EDF2] bg-white p-5 transition-all duration-150 hover:border-[#D7DEE7] hover:shadow-[0_2px_8px_rgba(17,19,26,0.04)]">
      <p className="text-[13px] font-semibold uppercase tracking-[0.08em] text-[#8B95A5]">
        {label}
      </p>
      <h3 className={`mt-3 text-3xl font-bold tracking-tight font-[family-name:var(--font-space-grotesk)] font-tabular ${accent ? "text-[#0066FF]" : "text-[#11131A]"}`}>
        {value}
      </h3>
    </div>
  );
}

export function AnalyticsOverviewCard({
  overview,
}: Readonly<AnalyticsOverviewCardProps>) {
  return (
    <Card variant="elevated" padding="none">
      <div className="px-6 py-5 border-b border-[#F0F4F8]">
        <CardTitle>Analytics Overview</CardTitle>
        <CardDescription>Overall prediction performance summary</CardDescription>
      </div>

      <CardContent className="p-6">
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
          <MetricItem label="Total Predictions" value={overview.totalPredictions} />
          <MetricItem label="Completed" value={overview.completedPredictions} />
          <MetricItem label="Pending" value={overview.pendingPredictions} />
          <MetricItem label="Correct" value={overview.correctPredictions} accent />
          <MetricItem label="Incorrect" value={overview.incorrectPredictions} />
          <MetricItem label="Accuracy" value={`${overview.accuracy.toFixed(1)}%`} accent />
        </div>
      </CardContent>
    </Card>
  );
}