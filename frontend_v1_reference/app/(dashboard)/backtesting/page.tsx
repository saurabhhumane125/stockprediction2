"use client";

import { useEffect, useState } from "react";

import { ContentGrid } from "@/components/layout/ContentGrid";

import { StockSelector } from "@/features/dashboard/components/StockSelector";

import { useBacktesting } from "@/features/backtesting";

import { BacktestingLoading } from "@/features/backtesting/components/BacktestingLoading";
import { BacktestingError } from "@/features/backtesting/components/BacktestingError";
import { BacktestingEmpty } from "@/features/backtesting/components/BacktestingEmpty";
import { BacktestingSummaryCard } from "@/features/backtesting/components/BacktestingSummaryCard";
import { PerformanceCard } from "@/features/backtesting/components/PerformanceCard";
import { LatestPredictionCard } from "@/features/backtesting/components/LatestPredictionCard";

export default function BacktestingPage() {

  const [symbol, setSymbol] =
    useState("RELIANCE");

  const {

    data,

    loading,

    error,

    refresh,

  } = useBacktesting();

  useEffect(() => {

    refresh(symbol);

  }, [

    refresh,

    symbol,

  ]);

  if (loading) {

    return <BacktestingLoading />;

  }

  if (error) {

    return (

      <BacktestingError

        message={error}

      />

    );

  }

  if (!data) {

    return <BacktestingEmpty />;

  }

  return (

    <div className="space-y-8">

      <div className="rounded-[16px] border border-[#E8EDF2] bg-white p-5 shadow-sm">

        <StockSelector

          value={symbol}

          onChange={setSymbol}

        />

      </div>

      <ContentGrid>

        <div className="col-span-12">

          <BacktestingSummaryCard

            data={data}

          />

        </div>

        <div className="col-span-12 lg:col-span-6">

          <PerformanceCard

            data={data}

          />

        </div>

        <div className="col-span-12 lg:col-span-6">

          <LatestPredictionCard

            prediction={

              data.latestPrediction

            }

          />

        </div>

      </ContentGrid>

    </div>

  );

}