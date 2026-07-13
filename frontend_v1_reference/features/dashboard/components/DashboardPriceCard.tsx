import { TrendingUp } from "lucide-react";
import { Card, CardContent, CardLabel } from "@/components/ui/Card";
import type { LatestPriceViewModel } from "../types/dashboard.view.types";

interface Props {
  price: LatestPriceViewModel;
}

const metric = (label: string, value: string) => (
  <div>
    <p className="text-[13px] text-[#8B95A5] font-medium">{label}</p>
    <p className="mt-1 text-base font-semibold text-[#11131A] font-tabular">{value}</p>
  </div>
);

export function DashboardPriceCard({ price }: Props) {
  return (
    <Card className="h-full">
      <CardContent className="flex flex-col gap-5 h-full">

        {/* Header */}
        <div className="flex items-center justify-between">
          <CardLabel>Latest Price</CardLabel>
          <div className="flex h-8 w-8 items-center justify-center rounded-[8px] bg-[#F0F4F8]">
            <TrendingUp size={16} className="text-[#0066FF]" />
          </div>
        </div>

        {/* Primary price */}
        <div className="mt-2">
          <p className="text-4xl font-bold tracking-tight text-[#11131A] font-tabular font-[family-name:var(--font-space-grotesk)]">
            ₹{(price?.price ?? 0).toFixed(2)}
          </p>
          <p className="mt-1.5 text-[13px] text-[#8B95A5] font-medium">
            {price?.date ?? ""}
          </p>
        </div>

        {/* OHLV grid */}
        <div className="mt-auto grid grid-cols-2 gap-x-5 gap-y-4 border-t border-[#F0F4F8] pt-5">
          {metric("Open", `₹${(price?.open ?? 0).toFixed(2)}`)}
          {metric("High", `₹${(price?.high ?? 0).toFixed(2)}`)}
          {metric("Low", `₹${(price?.low ?? 0).toFixed(2)}`)}
          {metric("Volume", (price?.volume ?? 0).toLocaleString())}
        </div>

      </CardContent>
    </Card>
  );
}