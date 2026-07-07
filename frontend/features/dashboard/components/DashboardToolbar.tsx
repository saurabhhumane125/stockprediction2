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

    <div className="mb-8 flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:flex-row md:items-center md:justify-between">

      <StockSelector
        value={symbol}
        onChange={onSymbolChange}
      />

      <RefreshButton
        loading={loading}
        onRefresh={onRefresh}
      />

    </div>

  );

}