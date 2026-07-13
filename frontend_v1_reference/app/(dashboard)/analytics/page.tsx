"use client";

import { useEffect } from "react";

import { LoadingState } from "@/components/feedback/LoadingState";
import { ErrorState } from "@/components/feedback/ErrorState";
import { EmptyState } from "@/components/feedback/EmptyState";
import { ContentGrid } from "@/components/layout/ContentGrid";

import { useAnalytics } from "@/features/analytics";

import { AnalyticsOverviewCard } from "@/features/analytics/components/AnalyticsOverviewCard";
import { DistributionCard } from "@/features/analytics/components/DistributionCard";
import { ConfidenceCard } from "@/features/analytics/components/ConfidenceCard";
import { RecentPredictionsCard } from "@/features/analytics/components/RecentPredictionsCard";

export default function AnalyticsPage() {

  const {

    data,

    loading,

    error,

    refresh,

  } = useAnalytics();

  useEffect(() => {

    refresh();

  }, [refresh]);

  if (loading) {

    return (

      <LoadingState

        message="Loading analytics..."

      />

    );

  }

  if (error) {

    return (

      <ErrorState

        message={error}

      />

    );

  }

  if (!data) {

    return (

      <EmptyState

        title="Analytics Unavailable"

        description="No analytics data is currently available."

      />

    );

  }

  return (

    <ContentGrid>

      <div className="col-span-12">

        <AnalyticsOverviewCard

          overview={data.overview}

        />

      </div>

      <div className="col-span-12 xl:col-span-6">

        <DistributionCard

          distribution={data.distribution}

        />

      </div>

      <div className="col-span-12 xl:col-span-6">

        <ConfidenceCard

          confidence={data.confidence}

        />

      </div>

      <div className="col-span-12">

        <RecentPredictionsCard

          predictions={data.recent}

        />

      </div>

    </ContentGrid>

  );

}