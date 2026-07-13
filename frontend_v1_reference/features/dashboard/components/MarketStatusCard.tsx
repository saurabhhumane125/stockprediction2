import { Activity, Clock } from "lucide-react";
import { Card, CardContent, CardLabel } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

interface Props {
  marketOpen: boolean;
  lastUpdated: string;
}

export function MarketStatusCard({ marketOpen, lastUpdated }: Props) {
  return (
    <Card className="h-full">
      <CardContent className="flex flex-col gap-5 h-full">

        {/* Header */}
        <div className="flex items-center justify-between">
          <CardLabel>NSE Market</CardLabel>
          <div className="flex h-8 w-8 items-center justify-center rounded-[8px] bg-[#F0F4F8]">
            <Activity size={16} className="text-[#0066FF]" />
          </div>
        </div>

        {/* Status */}
        <div className="flex items-center justify-between mt-2">
          <h2 className="text-3xl font-bold tracking-tight text-[#11131A] font-[family-name:var(--font-space-grotesk)]">
            {marketOpen ? "Open" : "Closed"}
          </h2>
          <Badge variant={marketOpen ? "buy" : "neutral"} size="lg">
            {marketOpen ? "LIVE" : "CLOSED"}
          </Badge>
        </div>

        {/* Last updated */}
        <div className="flex items-center gap-3 border-t border-[#F0F4F8] pt-5 mt-auto">
          <div className="flex h-8 w-8 items-center justify-center rounded-[8px] bg-[#F7F9FC]">
             <Clock size={16} className="shrink-0 text-[#8B95A5]" />
          </div>
          <div>
            <p className="text-[13px] font-medium text-[#8B95A5]">Last updated</p>
            <p className="mt-0.5 text-[15px] font-semibold text-[#11131A]">
              {lastUpdated || "N/A"}
            </p>
          </div>
        </div>

      </CardContent>
    </Card>
  );
}