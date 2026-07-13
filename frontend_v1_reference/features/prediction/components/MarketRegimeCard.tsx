import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardLabel } from "@/components/ui/Card";
import type { PredictionViewModel } from "../types/prediction.view.types";

interface MarketRegimeCardProps {
  prediction: PredictionViewModel;
}

const Metric = ({ label, value }: { label: string; value: string }) => (
  <div>
    <p className="text-[13px] font-medium text-[#8B95A5]">{label}</p>
    <p className="mt-1 text-[15px] font-semibold text-[#11131A]">{value}</p>
  </div>
);

export function MarketRegimeCard({ prediction }: MarketRegimeCardProps) {
  if (!prediction.marketRegime) {
    return null;
  }

  const regime = prediction.marketRegime;

  return (
    <Card className="h-full">
      <CardContent className="space-y-5 h-full flex flex-col">
        <div className="flex items-center justify-between">
          <CardLabel>Market Regime</CardLabel>
          <Badge variant="primary" size="lg">{regime.regime}</Badge>
        </div>

        <div className="grid grid-cols-2 gap-4 rounded-[12px] bg-[#F7F9FC] p-5 mt-auto">
          <Metric label="Trend" value={regime.trend} />
          <Metric label="Strength" value={regime.trendStrength} />
          <Metric label="Volatility" value={regime.volatility} />
          <Metric label="Momentum" value={regime.momentum} />
        </div>
      </CardContent>
    </Card>
  );
}