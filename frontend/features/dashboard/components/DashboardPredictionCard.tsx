import {
  BrainCircuit,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";

import {
  Card,
  CardContent,
} from "@/components/ui/Card";

import { Badge } from "@/components/ui/Badge";

import type {
  PredictionViewModel,
} from "../types/dashboard.view.types";

interface Props {

  prediction: PredictionViewModel;

}

export function DashboardPredictionCard({

  prediction,

}: Props) {

  const badgeVariant =
    prediction.prediction === "BUY"
      ? "buy"
      : prediction.prediction === "SELL"
      ? "sell"
      : "neutral";

  const Icon =
    prediction.prediction === "BUY"
      ? TrendingUp
      : prediction.prediction === "SELL"
      ? TrendingDown
      : Minus;

  return (

    <Card
      variant="elevated"
      className="
        h-full
        overflow-hidden
      "
    >

      <CardContent className="space-y-8">

        <div className="flex items-start justify-between">

          <div>

            <p className="text-sm font-medium text-[#5B6473]">

              AI Prediction

            </p>

            <h2 className="mt-2 text-4xl font-bold text-[#11131A]">

              {prediction.prediction}

            </h2>

          </div>

          <div
            className="
              rounded-2xl
              bg-[#EDF1F5]
              p-4
            "
          >

            <BrainCircuit
              className="text-[#0066FF]"
              size={28}
            />

          </div>

        </div>

        <Badge
          variant={badgeVariant}
          size="lg"
        >

          <Icon size={18} />

          {prediction.prediction}

        </Badge>

        <div>

          <div className="mb-2 flex justify-between">

            <span className="text-sm text-[#5B6473]">

              Confidence

            </span>

            <span className="font-semibold">

              {prediction.confidence.toFixed(2)}%

            </span>

          </div>

          <div
            className="
              h-3
              overflow-hidden
              rounded-full
              bg-[#EDF1F5]
            "
          >

            <div

              className="
                h-full
                rounded-full
                bg-[#0066FF]
              "

              style={{

                width: `${prediction.confidence}%`,

              }}

            />

          </div>

        </div>

      </CardContent>

    </Card>

  );

}