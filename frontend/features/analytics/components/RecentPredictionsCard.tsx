import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";

import { Badge } from "@/components/ui/Badge";

import type {
  RecentPredictionViewModel,
} from "../types/analytics.view.types";

interface RecentPredictionsCardProps {
  predictions: RecentPredictionViewModel[];
}

export function RecentPredictionsCard({
  predictions,
}: Readonly<RecentPredictionsCardProps>) {
  return (

    <Card
      variant="elevated"
      className="h-full"
    >

      <CardHeader>

        <div>

          <CardTitle>
            Recent Predictions
          </CardTitle>

          <CardDescription>
            Latest prediction history.
          </CardDescription>

        </div>

      </CardHeader>

      <CardContent>

        <div className="overflow-x-auto">

          <table className="min-w-full text-sm">

            <thead>

              <tr className="border-b border-slate-200 text-left">

                <th className="pb-3">
                  ID
                </th>

                <th className="pb-3">
                  Stock
                </th>

                <th className="pb-3">
                  Prediction
                </th>

                <th className="pb-3">
                  Status
                </th>

                <th className="pb-3">
                  Confidence
                </th>

                <th className="pb-3">
                  Date
                </th>

              </tr>

            </thead>

            <tbody>

              {predictions.map(
                (prediction) => (

                  <tr
                    key={prediction.id}
                    className="border-b border-slate-100"
                  >

                    <td className="py-4">
                      {prediction.id}
                    </td>

                    <td className="py-4">
                      {prediction.stockId}
                    </td>

                    <td className="py-4">

                      <Badge
                        variant={
                          prediction.prediction === "BUY"
                            ? "buy"
                            : "sell"
                        }
                      >
                        {prediction.prediction}
                      </Badge>

                    </td>

                    <td className="py-4">

                      <Badge
                        variant={
                          prediction.status === "COMPLETED"
                            ? "success"
                            : "warning"
                        }
                      >
                        {prediction.status}
                      </Badge>

                    </td>

                    <td className="py-4">
                      {(prediction.confidence * 100).toFixed(2)}%
                    </td>

                    <td className="py-4">
                      {new Date(
                        prediction.createdAt,
                      ).toLocaleString()}
                    </td>

                  </tr>

                ),
              )}

              {predictions.length === 0 && (

                <tr>

                  <td
                    colSpan={6}
                    className="py-8 text-center text-slate-500"
                  >
                    No prediction history available.
                  </td>

                </tr>

              )}

            </tbody>

          </table>

        </div>

      </CardContent>

    </Card>

  );
}