import { CandlestickChart } from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { StockViewModel } from "../types/stock.view.types";

interface StockCardProps {
  stock: StockViewModel;
}

export function StockCard({ stock }: Readonly<StockCardProps>) {
  return (
    <Card hoverable className="p-6">
      <CardContent className="space-y-4">
        {/* Header: icon + sector */}
        <div className="flex items-start justify-between">
          <div className="flex h-10 w-10 items-center justify-center rounded-[10px] bg-[#F0F4F8]">
            <CandlestickChart size={20} className="text-[#0066FF]" />
          </div>
          <Badge variant="neutral" size="lg">{stock.sector ?? "—"}</Badge>
        </div>

        {/* Symbol */}
        <div>
          <p className="text-xl font-bold text-[#11131A] font-[family-name:var(--font-space-grotesk)] tracking-tight">
            {stock.symbol}
          </p>
          <p className="mt-1 text-[14px] text-[#5B6473] leading-snug">
            {stock.companyName}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}