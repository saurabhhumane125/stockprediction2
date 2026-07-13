import {
  Card,
  CardContent,
  CardDescription,
  CardTitle,
} from "@/components/ui/Card";

import type { ConfidenceViewModel } from "../types/analytics.view.types";

interface ConfidenceCardProps {
  confidence: ConfidenceViewModel;
}

interface ConfidenceMetricProps {
  title: string;
  value: number;
}

function ConfidenceMetric({ title, value }: Readonly<ConfidenceMetricProps>) {
  return (
    <div className="rounded-[12px] border border-[#E8EDF2] bg-white p-5 transition-all duration-150 hover:border-[#D7DEE7] hover:shadow-[0_2px_8px_rgba(17,19,26,0.04)]">
      <p className="text-[13px] font-semibold uppercase tracking-[0.08em] text-[#8B95A5]">
        {title}
      </p>
      <h3 className="mt-3 text-3xl font-bold tracking-tight text-[#11131A] font-[family-name:var(--font-space-grotesk)] font-tabular">
        {(value * 100).toFixed(1)}%
      </h3>
    </div>
  );
}

export function ConfidenceCard({ confidence }: Readonly<ConfidenceCardProps>) {
  return (
    <Card variant="elevated" padding="none">
      <div className="px-6 py-5 border-b border-[#F0F4F8]">
        <CardTitle>Confidence Statistics</CardTitle>
        <CardDescription>Confidence distribution across all predictions</CardDescription>
      </div>

      <CardContent className="p-6">
        <div className="grid gap-4 md:grid-cols-3">
          <ConfidenceMetric title="Average" value={confidence.average} />
          <ConfidenceMetric title="Minimum" value={confidence.minimum} />
          <ConfidenceMetric title="Maximum" value={confidence.maximum} />
        </div>
      </CardContent>
    </Card>
  );
}