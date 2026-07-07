import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

import type { PredictionViewModel } from "../types/prediction.view.types";

interface PredictionResultCardProps {

  prediction: PredictionViewModel;

}

export function PredictionResultCard({

  prediction,

}: PredictionResultCardProps) {

  const badgeVariant =

    prediction.prediction === "BUY"

      ? "buy"

      : prediction.prediction === "SELL"

      ? "sell"

      : "neutral";

  return (

    <Card className="space-y-6">

      <div className="flex items-center justify-between">

        <h2 className="text-xl font-bold">

          Live Prediction

        </h2>

        <Badge variant={badgeVariant}>

          {prediction.prediction}

        </Badge>

      </div>

      <div className="grid grid-cols-2 gap-4">

        <div>

          <p className="text-sm text-slate-500">

            Confidence

          </p>

          <p className="text-2xl font-bold">

            {(prediction.confidence * 100).toFixed(2)}%

          </p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Stock

          </p>

          <p className="text-2xl font-bold">

            {prediction.stock}

          </p>

        </div>

      </div>

      <div className="grid grid-cols-2 gap-4">

        <div>

          <p className="text-sm text-slate-500">

            Buy Probability

          </p>

          <p className="font-semibold">

            {prediction.probabilityBuy !== null

              ? `${(prediction.probabilityBuy * 100).toFixed(2)}%`

              : "N/A"}

          </p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Sell Probability

          </p>

          <p className="font-semibold">

            {prediction.probabilitySell !== null

              ? `${(prediction.probabilitySell * 100).toFixed(2)}%`

              : "N/A"}

          </p>

        </div>

      </div>

      <div>

        <p className="text-sm text-slate-500">

          Technical Signal

        </p>

        <p>

          {prediction.technicalSignal ?? "N/A"}

        </p>

      </div>

      <div>

        <p className="text-sm text-slate-500">

          News Signal

        </p>

        <p>

          {prediction.newsSignal ?? "N/A"}

        </p>

      </div>

      <div>

        <p className="text-sm text-slate-500">

          Final Reason

        </p>

        <p>

          {prediction.finalReason ?? "N/A"}

        </p>

      </div>

    </Card>

  );

}