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
  const total = distribution.buy + distribution.sell;
  const buyPercentage = total === 0 ? 0 : (distribution.buy / total) * 100;
  const sellPercentage = total === 0 ? 0 : (distribution.sell / total) * 100;

  return (
    <Card variant="elevated">
      <CardHeader>
        <div>
          <CardTitle>Prediction Distribution</CardTitle>
          <CardDescription>BUY vs SELL predictions.</CardDescription>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div>
          <div className="mb-2 flex items-center justify-between">
            <Badge variant="buy" size="lg">BUY</Badge>
            <span className="text-[15px] font-bold text-[#11131A] font-tabular">{distribution.buy}</span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-[#F0F4F8]">
            <div
              className="h-full rounded-full bg-[#B4FF00] transition-all duration-300"
              style={{ width: `${buyPercentage}%` }}
            />
          </div>
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <Badge variant="sell" size="lg">SELL</Badge>
            <span className="text-[15px] font-bold text-[#11131A] font-tabular">{distribution.sell}</span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-[#F0F4F8]">
            <div
              className="h-full rounded-full bg-[#FF3B3B] transition-all duration-300"
              style={{ width: `${sellPercentage}%` }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}