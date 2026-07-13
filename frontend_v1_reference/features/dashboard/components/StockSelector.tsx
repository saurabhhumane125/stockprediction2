"use client";

import { useEffect } from "react";
import { useStocks } from "@/features/stocks/hooks/useStocks";

interface StockSelectorProps {
  value: string;
  onChange: (symbol: string) => void;
}

export function StockSelector({
  value,
  onChange,
}: StockSelectorProps) {
  const {
    stocks,
    loading,
    error,
  } = useStocks();

  useEffect(() => {
    if (
      !loading &&
      !error &&
      stocks.length > 0 &&
      !stocks.some(
        (stock) => stock.symbol === value,
      )
    ) {
      onChange(stocks[0].symbol);
    }
  }, [loading, error, stocks, value, onChange]);

  if (loading) {
    return (
      <select
        disabled
        className="h-11 w-full rounded-[10px] border border-[#E8EDF2] bg-[#F7F9FC] px-4 text-[15px] font-medium text-[#5B6473]"
      >
        <option>Loading stocks...</option>
      </select>
    );
  }

  if (error) {
    return (
      <select
        disabled
        className="h-11 w-full rounded-[10px] border border-[#FFE5E5] bg-[#FFFBFB] px-4 text-[15px] font-medium text-[#FF3B3B]"
      >
        <option>Failed to load stocks</option>
      </select>
    );
  }

  return (
    <select
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className="h-11 w-full rounded-[10px] border border-[#E8EDF2] bg-white px-4 text-[15px] font-medium text-[#11131A] outline-none transition-all duration-150 hover:border-[#D7DEE7] focus:border-[#0066FF] focus:ring-[3px] focus:ring-[#0066FF]/10 shadow-[0_1px_2px_rgba(17,19,26,0.02)_inset]"
    >
      {stocks.map((stock) => (
        <option key={stock.id} value={stock.symbol}>
          {stock.symbol}
        </option>
      ))}
    </select>
  );
}