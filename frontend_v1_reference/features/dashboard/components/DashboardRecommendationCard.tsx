import { Sparkles } from "lucide-react";
import { Card, CardContent, CardLabel } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { RecommendationViewModel } from "../types/dashboard.view.types";

interface Props {
  recommendation: RecommendationViewModel;
}

export function DashboardRecommendationCard({ recommendation }: Props) {
  const action = recommendation?.action ?? "NEUTRAL";
  const isBuy = action.includes("BUY");
  const isSell = action.includes("SELL");
  const badgeVariant = isBuy ? "buy" : isSell ? "sell" : "hold";

  const confidence = ((recommendation?.confidence ?? 0) * 100).toFixed(1);

  return (
    <Card className="h-full">
      <CardContent className="flex flex-col gap-5 h-full">

        {/* Header */}
        <div className="flex items-center justify-between">
          <CardLabel>Recommendation</CardLabel>
          <div className="flex h-8 w-8 items-center justify-center rounded-[8px] bg-[#F0F4F8]">
            <Sparkles size={16} className="text-[#0066FF]" />
          </div>
        </div>

        {/* Action */}
        <div className="flex items-start justify-between gap-4 mt-2">
          <h2 className="text-3xl font-bold tracking-tight text-[#11131A] font-[family-name:var(--font-space-grotesk)]">
            {action.replaceAll("_", " ")}
          </h2>
          <Badge variant={badgeVariant} size="lg">
            {recommendation?.strength ?? "N/A"}
          </Badge>
        </div>

        {/* Signal grid */}
        <div className="grid grid-cols-2 gap-4 rounded-[12px] bg-[#F7F9FC] p-5 mt-2">
          <div>
            <p className="text-[13px] font-medium text-[#8B95A5]">Confidence</p>
            <p className="mt-1 text-[15px] font-bold text-[#11131A] font-tabular">{confidence}%</p>
          </div>
          <div>
            <p className="text-[13px] font-medium text-[#8B95A5]">Sentiment</p>
            <p className="mt-1 text-[15px] font-semibold text-[#11131A]">{recommendation?.sentiment ?? "—"}</p>
          </div>
          <div>
            <p className="text-[13px] font-medium text-[#8B95A5]">Technical</p>
            <p className="mt-1 text-[15px] font-semibold text-[#11131A]">{recommendation?.technicalSignal ?? "—"}</p>
          </div>
          <div>
            <p className="text-[13px] font-medium text-[#8B95A5]">News Signal</p>
            <p className="mt-1 text-[15px] font-semibold text-[#11131A]">{recommendation?.newsSignal ?? "—"}</p>
          </div>
        </div>

        {/* Summary */}
        {recommendation?.summary && (
          <div className="border-t border-[#F0F4F8] pt-5 mt-2">
            <p className="text-[13px] font-semibold text-[#8B95A5] mb-2 uppercase tracking-wide">Summary</p>
            <p className="text-base leading-relaxed text-[#11131A]">
              {recommendation.summary}
            </p>
          </div>
        )}

        {/* Reason */}
        {recommendation?.reason && (
          <div className="border-t border-[#F0F4F8] pt-5 mt-auto">
            <p className="text-[13px] font-semibold text-[#8B95A5] mb-2 uppercase tracking-wide">AI Reasoning</p>
            <p className="text-[15px] leading-relaxed text-[#5B6473]">
              {recommendation.reason}
            </p>
          </div>
        )}

      </CardContent>
    </Card>
  );
}