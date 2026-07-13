import { BrainCircuit, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card, CardContent, CardLabel } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { PredictionViewModel } from "../types/dashboard.view.types";

interface Props {
  prediction: PredictionViewModel;
}

export function DashboardPredictionCard({ prediction }: Props) {
  const pred = prediction?.prediction ?? "NEUTRAL";
  const confidence = prediction?.confidence ?? 0;

  const isBuy = pred === "BUY";
  const isSell = pred === "SELL";

  const badgeVariant = isBuy ? "buy" : isSell ? "sell" : "hold";
  const Icon = isBuy ? TrendingUp : isSell ? TrendingDown : Minus;

  const confidenceColor = isBuy
    ? "#B4FF00"
    : isSell
    ? "#FF3B3B"
    : "#8B95A5";

  return (
    <Card variant="elevated" className="h-full">
      <CardContent className="flex flex-col h-full gap-5">

        {/* Header */}
        <div className="flex items-center justify-between">
          <CardLabel>AI Prediction</CardLabel>
          <div className="flex h-8 w-8 items-center justify-center rounded-[8px] bg-[#F0F4F8]">
            <BrainCircuit size={16} className="text-[#0066FF]" />
          </div>
        </div>

        {/* Primary result */}
        <div className="flex items-end justify-between mt-2">
          <h2 className="text-3xl font-bold tracking-tight text-[#11131A] font-[family-name:var(--font-space-grotesk)]">
            {pred}
          </h2>
          <Badge variant={badgeVariant} size="lg" className="flex items-center gap-1.5">
            <Icon size={14} strokeWidth={2.5} />
            {pred}
          </Badge>
        </div>

        {/* Confidence bar */}
        <div className="space-y-3 border-t border-[#F0F4F8] pt-5 mt-auto">
          <div className="flex items-center justify-between">
            <span className="text-[13px] font-medium text-[#8B95A5]">Confidence</span>
            <span className="text-[15px] font-bold text-[#11131A] font-tabular">{confidence.toFixed(1)}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-[#F0F4F8]">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${confidence}%`,
                background: confidenceColor,
              }}
            />
          </div>
        </div>

        {/* Supporting signals */}
        {(prediction?.sentiment || prediction?.technicalSignal) && (
          <div className="grid grid-cols-2 gap-4 border-t border-[#F0F4F8] pt-4">
            {prediction.sentiment && (
              <div>
                <p className="text-[13px] font-medium text-[#8B95A5]">Sentiment</p>
                <p className="mt-1 text-[15px] font-semibold text-[#11131A]">
                  {prediction.sentiment}
                </p>
              </div>
            )}
            {prediction.technicalSignal && (
              <div>
                <p className="text-[13px] font-medium text-[#8B95A5]">Technical</p>
                <p className="mt-1 text-[15px] font-semibold text-[#11131A]">
                  {prediction.technicalSignal}
                </p>
              </div>
            )}
          </div>
        )}

      </CardContent>
    </Card>
  );
}