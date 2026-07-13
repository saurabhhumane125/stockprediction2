import { Card, CardContent, CardLabel } from "@/components/ui/Card";
import type { PredictionViewModel } from "../types/prediction.view.types";

interface LatestCandleCardProps {
  prediction: PredictionViewModel;
}

const Metric = ({ label, value }: { label: string; value: string }) => (
  <div>
    <p className="text-[13px] font-medium text-[#8B95A5]">{label}</p>
    <p className="mt-1 text-[15px] font-semibold text-[#11131A] font-tabular">{value}</p>
  </div>
);

export function LatestCandleCard({ prediction }: LatestCandleCardProps) {
  if (!prediction.latestCandle) {
    return null;
  }

  const candle = prediction.latestCandle;

  return (
    <Card className="h-full">
      <CardContent className="space-y-5 flex flex-col h-full">
        <CardLabel>Latest Market Candle</CardLabel>

        <div className="grid grid-cols-2 gap-4 rounded-[12px] bg-[#F7F9FC] p-5 mt-auto">
          <Metric label="Date" value={candle.date} />
          <Metric label="Volume" value={candle.volume.toLocaleString()} />
          <Metric label="Open" value={`₹${candle.open.toFixed(2)}`} />
          <Metric label="High" value={`₹${candle.high.toFixed(2)}`} />
          <Metric label="Low" value={`₹${candle.low.toFixed(2)}`} />
          <Metric label="Close" value={`₹${candle.close.toFixed(2)}`} />
        </div>
      </CardContent>
    </Card>
  );
}