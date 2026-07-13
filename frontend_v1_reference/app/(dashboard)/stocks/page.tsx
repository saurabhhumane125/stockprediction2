"use client";

import { mapStocks } from "@/features/stocks/types/stock.mapper";

import { useStocks } from "@/features/stocks";

import { StockGrid } from "@/features/stocks/components/StockGrid";

import { StockLoading } from "@/features/stocks/components/StockLoading";

import { StockError } from "@/features/stocks/components/StockError";

import { StockEmpty } from "@/features/stocks/components/StockEmpty";

export default function StocksPage() {

  const {

    stocks,

    loading,

    error,

  } = useStocks();

  if (loading) {

    return <StockLoading />;

  }

  if (error) {

    return (

      <StockError

        message={error}

      />

    );

  }

  if (stocks.length === 0) {

    return <StockEmpty />;

  }

  return (

    <StockGrid

      stocks={

        mapStocks(stocks)

      }

    />

  );

}