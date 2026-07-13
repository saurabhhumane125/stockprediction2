"use client";

import { useState } from "react";

import { PageHeader } from "@/components/layout/PageHeader";
import { DashboardGrid } from "@/features/dashboard/components/DashboardGrid";
import { DashboardToolbar } from "@/features/dashboard/components/DashboardToolbar";

import { DashboardLoading } from "@/features/dashboard/components/DashboardLoading";
import { DashboardError } from "@/features/dashboard/components/DashboardError";
import { DashboardEmpty } from "@/features/dashboard/components/DashboardEmpty";

import { DashboardPredictionCard } from "@/features/dashboard/components/DashboardPredictionCard";
import { DashboardPriceCard } from "@/features/dashboard/components/DashboardPriceCard";
import { DashboardRecommendationCard } from "@/features/dashboard/components/DashboardRecommendationCard";
import { MarketStatusCard } from "@/features/dashboard/components/MarketStatusCard";

import { useDashboard } from "@/features/dashboard/hooks/useDashboard";

export default function DashboardPage() {

  const [

    symbol,

    setSymbol,

  ] = useState("RELIANCE");

  const {

    data,

    loading,

    error,

    refresh,

  } = useDashboard(symbol);

  return (

    <>

      <PageHeader
        title="Dashboard"
        subtitle="Real-time market overview, AI prediction confidence, recommendation insights and latest market activity."
        breadcrumbs={[
          {
            label: "Home",
            href: "/dashboard",
          },
          {
            label: "Dashboard",
          },
        ]}
      />

      <DashboardToolbar
        symbol={symbol}
        loading={loading}
        onSymbolChange={setSymbol}
        onRefresh={() => {

          void refresh();

        }}
      />

      {loading && <DashboardLoading />}

      {!loading && error && (

        <DashboardError

          message={error}

        />

      )}

      {!loading && !error && !data && (

        <DashboardEmpty />

      )}

      {!loading && !error && data && (

        <DashboardGrid>

          {data.prediction && (

            <div className="col-span-12 xl:col-span-6">

              <DashboardPredictionCard

                prediction={data.prediction}

              />

            </div>

          )}

          {data.latestPrice && (

            <div className="col-span-12 xl:col-span-6">

              <DashboardPriceCard

                price={data.latestPrice}

              />

            </div>

          )}

          {data.recommendation && (

            <div className="col-span-12 lg:col-span-6">

              <DashboardRecommendationCard

                recommendation={data.recommendation}

              />

            </div>

          )}

          {data.latestPrice && (

            <div className="col-span-12 lg:col-span-6">

              <MarketStatusCard

                marketOpen={false}

                lastUpdated={data.latestPrice.date}

              />

            </div>

          )}

        </DashboardGrid>

      )}

    </>

  );

}