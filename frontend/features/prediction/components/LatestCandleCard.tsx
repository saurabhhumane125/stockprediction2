import { Card } from "@/components/ui/Card";

import type { PredictionViewModel } from "../types/prediction.view.types";

interface LatestCandleCardProps {

  prediction: PredictionViewModel;

}

export function LatestCandleCard({

  prediction,

}: LatestCandleCardProps) {

  if (!prediction.latestCandle) {

    return null;

  }

  const candle = prediction.latestCandle;

  return (

    <Card className="space-y-6">

      <h2 className="text-xl font-bold">

        Latest Market Candle

      </h2>

      <div className="grid grid-cols-2 gap-4">

        <div>

          <p className="text-sm text-slate-500">

            Date

          </p>

          <p>{candle.date}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Volume

          </p>

          <p>{candle.volume.toLocaleString()}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Open

          </p>

          <p>{candle.open.toFixed(2)}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            High

          </p>

          <p>{candle.high.toFixed(2)}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Low

          </p>

          <p>{candle.low.toFixed(2)}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Close

          </p>

          <p>{candle.close.toFixed(2)}</p>

        </div>

      </div>

    </Card>

  );

}