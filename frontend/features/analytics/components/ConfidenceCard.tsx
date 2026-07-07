import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";

import type {
  ConfidenceViewModel,
} from "../types/analytics.view.types";

interface ConfidenceCardProps {
  confidence: ConfidenceViewModel;
}

interface ConfidenceMetricProps {
  title: string;
  value: number;
}

function ConfidenceMetric({
  title,
  value,
}: Readonly<ConfidenceMetricProps>) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">

      <p className="text-sm font-medium text-slate-500">
        {title}
      </p>

      <h3 className="mt-3 text-3xl font-bold text-[#11131A]">
        {(value * 100).toFixed(2)}%
      </h3>

    </div>
  );
}

export function ConfidenceCard({
  confidence,
}: Readonly<ConfidenceCardProps>) {
  return (

    <Card variant="elevated">

      <CardHeader>

        <div>

          <CardTitle>
            Confidence Statistics
          </CardTitle>

          <CardDescription>
            Confidence distribution across all predictions.
          </CardDescription>

        </div>

      </CardHeader>

      <CardContent>

        <div className="grid gap-4 md:grid-cols-3">

          <ConfidenceMetric
            title="Average"
            value={confidence.average}
          />

          <ConfidenceMetric
            title="Minimum"
            value={confidence.minimum}
          />

          <ConfidenceMetric
            title="Maximum"
            value={confidence.maximum}
          />

        </div>

      </CardContent>

    </Card>

  );
}