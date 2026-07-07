import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

import type { PredictionViewModel } from "../types/prediction.view.types";

interface MarketRegimeCardProps {

  prediction: PredictionViewModel;

}

export function MarketRegimeCard({

  prediction,

}: MarketRegimeCardProps) {

  if (!prediction.marketRegime) {

    return null;

  }

  const regime = prediction.marketRegime;

  return (

    <Card className="space-y-6">

      <div className="flex items-center justify-between">

        <h2 className="text-xl font-bold">

          Market Regime

        </h2>

        <Badge variant="primary">

          {regime.regime}

        </Badge>

      </div>

      <div className="grid grid-cols-2 gap-4">

        <div>

          <p className="text-sm text-slate-500">

            Trend

          </p>

          <p>{regime.trend}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Strength

          </p>

          <p>{regime.trendStrength}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Volatility

          </p>

          <p>{regime.volatility}</p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Momentum

          </p>

          <p>{regime.momentum}</p>

        </div>

      </div>

    </Card>

  );

}