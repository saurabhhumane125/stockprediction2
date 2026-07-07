import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";

import { Badge } from "@/components/ui/Badge";

import type {
  DistributionViewModel,
} from "../types/analytics.view.types";

interface DistributionCardProps {
  distribution: DistributionViewModel;
}

export function DistributionCard({
  distribution,
}: Readonly<DistributionCardProps>) {

  const total =
    distribution.buy +
    distribution.sell;

  const buyPercentage =
    total === 0
      ? 0
      : (distribution.buy / total) * 100;

  const sellPercentage =
    total === 0
      ? 0
      : (distribution.sell / total) * 100;

  return (

    <Card variant="elevated">

      <CardHeader>

        <div>

          <CardTitle>
            Prediction Distribution
          </CardTitle>

          <CardDescription>
            BUY vs SELL predictions.
          </CardDescription>

        </div>

      </CardHeader>

      <CardContent className="space-y-8">

        <div>

          <div className="mb-2 flex items-center justify-between">

            <Badge variant="buy">
              BUY
            </Badge>

            <span className="font-semibold">
              {distribution.buy}
            </span>

          </div>

          <div className="h-3 overflow-hidden rounded-full bg-slate-100">

            <div
              className="h-full rounded-full bg-lime-400 transition-all duration-300"
              style={{
                width: `${buyPercentage}%`,
              }}
            />

          </div>

        </div>

        <div>

          <div className="mb-2 flex items-center justify-between">

            <Badge variant="sell">
              SELL
            </Badge>

            <span className="font-semibold">
              {distribution.sell}
            </span>

          </div>

          <div className="h-3 overflow-hidden rounded-full bg-slate-100">

            <div
              className="h-full rounded-full bg-red-500 transition-all duration-300"
              style={{
                width: `${sellPercentage}%`,
              }}
            />

          </div>

        </div>

      </CardContent>

    </Card>

  );

}