"use client";

import { Button } from "@/components/ui/Button";
import { StockSelector } from "@/features/dashboard/components/StockSelector";

interface PredictionToolbarProps {
  symbol: string;
  loading: boolean;
  onPredict: () => void;
  onSymbolChange: (symbol: string) => void;
}

export function PredictionToolbar({
  symbol,
  loading,
  onPredict,
  onSymbolChange,
}: PredictionToolbarProps) {
  return (
    <div className="mb-5 flex flex-col gap-3 rounded-[12px] border border-[#E8EDF2] bg-white p-3.5 md:flex-row md:items-center md:justify-between shadow-[0_1px_2px_rgba(17,19,26,0.03)]">
      <StockSelector
        value={symbol}
        onChange={onSymbolChange}
      />
      <Button
        loading={loading}
        onClick={onPredict}
        size="sm"
      >
        Predict
      </Button>
    </div>
  );
}