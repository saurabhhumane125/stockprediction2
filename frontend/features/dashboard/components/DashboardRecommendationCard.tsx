import {
  Sparkles,
} from "lucide-react";

import {
  Card,
  CardContent,
} from "@/components/ui/Card";

import { Badge } from "@/components/ui/Badge";

import type {
  RecommendationViewModel,
} from "../types/dashboard.view.types";

interface Props {

  recommendation: RecommendationViewModel;

}

export function DashboardRecommendationCard({

  recommendation,

}: Props) {

  const badgeVariant =

    recommendation.action.includes("BUY")

      ? "buy"

      : recommendation.action.includes("SELL")

      ? "sell"

      : "neutral";

  return (

    <Card
      variant="elevated"
      className="h-full"
    >

      <CardContent className="space-y-8">

        <div className="flex items-start justify-between">

          <div>

            <p className="text-sm font-medium text-[#5B6473]">

              Recommendation

            </p>

            <h2 className="mt-2 text-3xl font-bold text-[#11131A]">

              {recommendation.action.replaceAll("_", " ")}

            </h2>

          </div>

          <div
            className="
              rounded-2xl
              bg-[#EDF1F5]
              p-4
            "
          >

            <Sparkles
              size={28}
              className="text-[#0066FF]"
            />

          </div>

        </div>

        <Badge
          variant={badgeVariant}
          size="lg"
        >

          {recommendation.action.replaceAll("_", " ")}

        </Badge>

        <div className="grid grid-cols-2 gap-6">

          <div>

            <p className="text-sm text-[#5B6473]">

              Confidence

            </p>

            <p className="mt-1 text-lg font-semibold">

              {(recommendation.confidence * 100).toFixed(2)}%

            </p>

          </div>

          <div>

            <p className="text-sm text-[#5B6473]">

              Strength

            </p>

            <p className="mt-1 text-lg font-semibold">

              {recommendation.strength}

            </p>

          </div>

          <div>

            <p className="text-sm text-[#5B6473]">

              Sentiment

            </p>

            <p className="mt-1 text-lg font-semibold">

              {recommendation.sentiment}

            </p>

          </div>

          <div>

            <p className="text-sm text-[#5B6473]">

              Score

            </p>

            <p className="mt-1 text-lg font-semibold">

              {recommendation.sentimentScore.toFixed(2)}

            </p>

          </div>

        </div>

        <div>

          <p className="text-sm font-medium text-[#5B6473]">

            Summary

          </p>

          <p className="mt-2 leading-7 text-[#11131A]">

            {recommendation.summary}

          </p>

        </div>

        <div>

          <p className="text-sm font-medium text-[#5B6473]">

            AI Reasoning

          </p>

          <p className="mt-2 leading-7 text-[#11131A]">

            {recommendation.reason}

          </p>

        </div>

      </CardContent>

    </Card>

  );

}