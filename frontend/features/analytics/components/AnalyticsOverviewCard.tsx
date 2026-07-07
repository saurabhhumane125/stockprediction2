import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";

import type {
  AnalyticsOverviewViewModel,
} from "../types/analytics.view.types";

interface AnalyticsOverviewCardProps {
  overview: AnalyticsOverviewViewModel;
}

interface MetricCardProps {
  label: string;
  value: number | string;
}

function MetricCard({
  label,
  value,
}: Readonly<MetricCardProps>) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 transition hover:border-[#0066FF] hover:bg-blue-50">
      <p className="text-sm font-medium text-slate-500">
        {label}
      </p>

      <h3 className="mt-3 text-3xl font-bold text-[#11131A]">
        {value}
      </h3>
    </div>
  );
}

export function AnalyticsOverviewCard({
  overview,
}: Readonly<AnalyticsOverviewCardProps>) {
  return (
    <Card variant="elevated">

      <CardHeader>

        <div>

          <CardTitle>
            Analytics Overview
          </CardTitle>

          <CardDescription>
            Overall prediction performance.
          </CardDescription>

        </div>

      </CardHeader>

      <CardContent>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">

          <MetricCard
            label="Total Predictions"
            value={overview.totalPredictions}
          />

          <MetricCard
            label="Completed"
            value={overview.completedPredictions}
          />

          <MetricCard
            label="Pending"
            value={overview.pendingPredictions}
          />

          <MetricCard
            label="Correct"
            value={overview.correctPredictions}
          />

          <MetricCard
            label="Incorrect"
            value={overview.incorrectPredictions}
          />

          <MetricCard
            label="Accuracy"
            value={`${overview.accuracy.toFixed(2)}%`}
          />

        </div>

      </CardContent>

    </Card>
  );
}