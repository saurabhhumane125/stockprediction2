"use client";

import { useState } from "react";

import { usePrediction } from "@/features/prediction";

import { PredictionToolbar } from "@/features/prediction/components/PredictionToolbar";
import { PredictionGrid } from "@/features/prediction/components/PredictionGrid";

import { PredictionLoading } from "@/features/prediction/components/PredictionLoading";
import { PredictionError } from "@/features/prediction/components/PredictionError";
import { PredictionEmpty } from "@/features/prediction/components/PredictionEmpty";

import { PredictionResultCard } from "@/features/prediction/components/PredictionResultCard";
import { LatestCandleCard } from "@/features/prediction/components/LatestCandleCard";
import { ExplanationCard } from "@/features/prediction/components/ExplanationCard";
import { MarketRegimeCard } from "@/features/prediction/components/MarketRegimeCard";

export default function PredictionPage() {

  const [

    symbol,

    setSymbol,

  ] = useState("RELIANCE");

  const {

    data,

    loading,

    error,

    predict,

  } = usePrediction();

  return (

    <div className="space-y-8">

      <PredictionToolbar

        symbol={symbol}

        loading={loading}

        onSymbolChange={setSymbol}

        onPredict={() => {

          void predict(symbol);

        }}

      />

      {

        loading &&

        <PredictionLoading />

      }

      {

        !loading && error && (

          <PredictionError

            message={error}

          />

        )

      }

      {

        !loading &&

        !error &&

        !data && (

          <PredictionEmpty />

        )

      }

      {

        !loading &&

        !error &&

        data && (

          <PredictionGrid>

            <div className="col-span-12 lg:col-span-6">

              <PredictionResultCard

                prediction={data}

              />

            </div>

            <div className="col-span-12 lg:col-span-6">

              <LatestCandleCard

                prediction={data}

              />

            </div>

            <div className="col-span-12 lg:col-span-6">

              <ExplanationCard

                prediction={data}

              />

            </div>

            <div className="col-span-12 lg:col-span-6">

              <MarketRegimeCard

                prediction={data}

              />

            </div>

          </PredictionGrid>

        )

      }

    </div>

  );

}