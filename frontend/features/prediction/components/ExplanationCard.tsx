import { Card } from "@/components/ui/Card";

import type { PredictionViewModel } from "../types/prediction.view.types";

interface ExplanationCardProps {

  prediction: PredictionViewModel;

}

export function ExplanationCard({

  prediction,

}: ExplanationCardProps) {

  if (!prediction.explanation) {

    return null;

  }

  const explanation = prediction.explanation;

  return (

    <Card className="space-y-6">

      <h2 className="text-xl font-bold">

        Technical Explanation

      </h2>

      <div className="grid grid-cols-2 gap-4">

        <div>

          <p className="text-sm text-slate-500">

            Trend

          </p>

          <p>{explanation.trend}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Trend Strength

          </p>

          <p>{explanation.trendStrength}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            RSI

          </p>

          <p>{explanation.rsi.toFixed(2)}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            RSI State

          </p>

          <p>{explanation.rsiState}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            ROC

          </p>

          <p>{explanation.roc.toFixed(2)}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Momentum

          </p>

          <p>{explanation.momentum.toFixed(2)}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            ATR

          </p>

          <p>{explanation.atr.toFixed(2)}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Volatility

          </p>

          <p>{explanation.volatility.toFixed(6)}</p>

        </div>

      </div>

      <div>

        <p className="mb-3 text-sm font-semibold text-slate-500">

          Summary

        </p>

        <ul className="list-disc space-y-2 pl-5">

          {explanation.summary.map((item) => (

            <li key={item}>

              {item}

            </li>

          ))}

        </ul>

      </div>

    </Card>

  );

}