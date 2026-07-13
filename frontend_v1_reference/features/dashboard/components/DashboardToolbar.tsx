"use client";

import { RefreshButton } from "./RefreshButton";
import { StockSelector } from "./StockSelector";

interface DashboardToolbarProps {
  symbol: string;
  loading: boolean;
  onSymbolChange: (symbol: string) => void;
  onRefresh: () => void;
}

export function DashboardToolbar({
  symbol,
  loading,
  onSymbolChange,
  onRefresh,
}: DashboardToolbarProps) {
  return (
    <div className="mb-6 flex flex-col gap-4 rounded-[16px] border border-[#E8EDF2] bg-white p-4 md:flex-row md:items-center md:justify-between shadow-[0_2px_8px_rgba(17,19,26,0.04)]">
      <div className="w-full md:w-64">
        <StockSelector
          value={symbol}
          onChange={onSymbolChange}
        />
      </div>
      <div className="shrink-0">
        <RefreshButton
          loading={loading}
          onRefresh={onRefresh}
        />
      </div>
    </div>
  );
}