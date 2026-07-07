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

    <div className="mb-8 flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:flex-row md:items-center md:justify-between">

      <StockSelector

        value={symbol}

        onChange={onSymbolChange}

      />

      <Button

        loading={loading}

        onClick={onPredict}

      >

        Predict

      </Button>

    </div>

  );

}