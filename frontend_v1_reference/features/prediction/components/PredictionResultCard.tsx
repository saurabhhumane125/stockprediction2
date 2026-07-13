import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card, CardContent, CardLabel } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { PredictionViewModel } from "../types/prediction.view.types";

interface PredictionResultCardProps {
  prediction: PredictionViewModel;
}

const Metric = ({ label, value }: { label: string; value: string }) => (
  <div>
    <p className="text-[13px] font-medium text-[#8B95A5]">{label}</p>
    <p className="mt-1 text-[15px] font-semibold text-[#11131A] font-tabular">{value}</p>
  </div>
);

export function PredictionResultCard({ prediction }: PredictionResultCardProps) {
  const pred = prediction.prediction ?? "NEUTRAL";
  const isBuy = pred === "BUY";
  const isSell = pred === "SELL";
  const badgeVariant = isBuy ? "buy" : isSell ? "sell" : "hold";
  const Icon = isBuy ? TrendingUp : isSell ? TrendingDown : Minus;
  const confidence = (prediction.confidence * 100).toFixed(1);

  const confidenceColor = isBuy ? "#B4FF00" : isSell ? "#FF3B3B" : "#8B95A5";

  return (
    <Card variant="elevated" className="h-full">
      <CardContent className="space-y-5 h-full flex flex-col">

        {/* Label */}
        <CardLabel>Live Prediction</CardLabel>

        {/* Primary result */}
        <div className="flex items-center justify-between py-1 mt-2">
          <h2 className="text-3xl font-bold tracking-tight text-[#11131A] font-[family-name:var(--font-space-grotesk)]">
            {pred}
          </h2>
          <Badge variant={badgeVariant} size="lg" className="flex items-center gap-1.5">
            <Icon size={14} strokeWidth={2.5} />
            {pred}
          </Badge>
        </div>

        {/* Confidence */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[13px] font-medium text-[#8B95A5]">Model confidence</span>
            <span className="text-[15px] font-bold text-[#11131A] font-tabular">{confidence}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-[#F0F4F8]">
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{ width: `${prediction.confidence * 100}%`, background: confidenceColor }}
            />
          </div>
        </div>

        {/* Signal grid */}
        <div className="grid grid-cols-2 gap-4 border-t border-[#F0F4F8] pt-5 mt-auto">
          <Metric label="Stock" value={prediction.stock} />
          <Metric
            label="Technical Signal"
            value={prediction.technicalSignal ?? "—"}
          />
          <Metric
            label="Buy Probability"
            value={prediction.probabilityBuy !== null
              ? `${(prediction.probabilityBuy * 100).toFixed(1)}%`
              : "—"}
          />
          <Metric
            label="Sell Probability"
            value={prediction.probabilitySell !== null
              ? `${(prediction.probabilitySell * 100).toFixed(1)}%`
              : "—"}
          />
          <Metric label="News Signal" value={prediction.newsSignal ?? "—"} />
        </div>

        {/* Final reason */}
        {prediction.finalReason && (
          <div className="border-t border-[#F0F4F8] pt-5 mt-2">
            <p className="text-[13px] font-semibold text-[#8B95A5] mb-2 uppercase tracking-wide">AI Reasoning</p>
            <p className="text-[15px] leading-relaxed text-[#5B6473]">{prediction.finalReason}</p>
          </div>
        )}

      </CardContent>
    </Card>
  );
}