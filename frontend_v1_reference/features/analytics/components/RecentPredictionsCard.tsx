import {
  Card,
  CardContent,
  CardDescription,
  CardTitle,
} from "@/components/ui/Card";

import { Badge } from "@/components/ui/Badge";

import type { RecentPredictionViewModel } from "../types/analytics.view.types";

interface RecentPredictionsCardProps {
  predictions: RecentPredictionViewModel[];
}

export function RecentPredictionsCard({
  predictions,
}: Readonly<RecentPredictionsCardProps>) {
  return (
    <Card padding="none" className="h-full">
      <div className="px-6 py-5 border-b border-[#F0F4F8]">
        <CardTitle>Recent Predictions</CardTitle>
        <CardDescription>Latest prediction history</CardDescription>
      </div>

      <CardContent>
        <div className="overflow-x-auto">
          <table className="min-w-full text-[15px]">
            <thead>
              <tr className="border-b border-[#F0F4F8] bg-[#F7F9FC]">
                {["ID", "Stock", "Prediction", "Status", "Confidence", "Date"].map((h) => (
                  <th
                    key={h}
                    className="px-6 py-4 text-left text-[13px] font-bold uppercase tracking-[0.06em] text-[#8B95A5] whitespace-nowrap"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F0F4F8]">
              {predictions.map((prediction) => (
                <tr
                  key={prediction.id}
                  className="transition-colors duration-100 hover:bg-[#FAFBFC]"
                >
                  <td className="px-6 py-4 text-[13px] text-[#8B95A5] font-mono">
                    #{prediction.id}
                  </td>
                  <td className="px-6 py-4 font-bold text-[#11131A]">
                    {prediction.stockId}
                  </td>
                  <td className="px-6 py-4">
                    <Badge
                      variant={
                        prediction.prediction === "BUY"
                          ? "buy"
                          : prediction.prediction === "SELL"
                          ? "sell"
                          : "hold"
                      }
                    >
                      {prediction.prediction}
                    </Badge>
                  </td>
                  <td className="px-6 py-4">
                    <Badge
                      variant={prediction.status === "COMPLETED" ? "success" : "warning"}
                    >
                      {prediction.status}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 font-bold text-[#11131A] font-tabular">
                    {(prediction.confidence * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 text-[#5B6473] whitespace-nowrap">
                    {new Date(prediction.createdAt).toLocaleString()}
                  </td>
                </tr>
              ))}

              {predictions.length === 0 && (
                <tr>
                  <td
                    colSpan={6}
                    className="px-6 py-12 text-center text-[15px] text-[#8B95A5]"
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