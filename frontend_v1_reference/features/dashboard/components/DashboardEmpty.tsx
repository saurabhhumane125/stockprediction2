import { BarChart3 } from "lucide-react";

export function DashboardEmpty() {
  return (
    <div className="flex flex-col items-center justify-center rounded-[16px] border border-dashed border-[#D7DEE7] bg-white py-16 text-center">
      <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-[10px] bg-[#F0F4F8]">
        <BarChart3 size={20} className="text-[#8B95A5]" />
      </div>
      <h3 className="text-[14px] font-semibold text-[#11131A] mb-1">
        No data available
      </h3>
      <p className="max-w-sm text-[13px] leading-5 text-[#5B6473]">
        Select a stock symbol above and click Refresh to load the latest prediction data.
      </p>
    </div>
  );
}