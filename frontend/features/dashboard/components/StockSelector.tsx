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

      onChange(

        stocks[0].symbol,

      );

    }

  }, [

    loading,

    error,

    stocks,

    value,

    onChange,

  ]);

  if (loading) {

    return (

      <select

        disabled

        className="h-11 rounded-xl border border-slate-300 bg-white px-4"

      >

        <option>

          Loading stocks...

        </option>

      </select>

    );

  }

  if (error) {

    return (

      <select

        disabled

        className="h-11 rounded-xl border border-red-300 bg-white px-4"

      >

        <option>

          Failed to load stocks

        </option>

      </select>

    );

  }

  return (

    <select

      value={value}

      onChange={(event) =>

        onChange(event.target.value)

      }

      className="h-11 rounded-xl border border-slate-300 bg-white px-4 text-sm font-medium outline-none transition focus:border-[#0066FF] focus:ring-2 focus:ring-blue-100"

    >

      {

        stocks.map((stock) => (

          <option

            key={stock.id}

            value={stock.symbol}

          >

            {stock.symbol}

          </option>

        ))

      }

    </select>

  );

}