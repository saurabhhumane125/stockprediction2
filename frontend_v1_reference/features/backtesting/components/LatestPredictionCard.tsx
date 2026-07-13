import {
  Card,
  CardContent,
  CardLabel,
} from "@/components/ui/Card";

import { Badge } from "@/components/ui/Badge";

import type {
  LatestPredictionViewModel,
} from "../types/backtesting.view.types";

interface Props {
  prediction: LatestPredictionViewModel | null;
}

export function LatestPredictionCard({
  prediction,
}: Readonly<Props>) {
  return (
    <Card className="h-full">
      <CardContent className="space-y-6">
        <CardLabel>Latest Prediction</CardLabel>

        {!prediction && (
          <p className="text-[15px] text-[#8B95A5]">No prediction available.</p>
        )}

        {prediction && (
          <div className="space-y-4">
            <div className="flex items-center justify-between py-1">
              <span className="text-[15px] text-[#5B6473] font-medium">Prediction</span>
              <Badge
                variant={
                  prediction.prediction === "BUY"
                    ? "buy"
                    : "sell"
                }
                size="lg"
              >
                {prediction.prediction}
              </Badge>
            </div>

            <div className="flex items-center justify-between py-2 border-b border-[#F0F4F8]">
              <span className="text-[15px] text-[#5B6473] font-medium">Confidence</span>
              <span className="text-base font-bold text-[#11131A] font-tabular">
                {(prediction.confidence * 100).toFixed(2)}%
              </span>
            </div>

            <div className="flex items-center justify-between py-2 border-b border-[#F0F4F8]">
              <span className="text-[15px] text-[#5B6473] font-medium">Result</span>
              <Badge variant={
                prediction.isCorrect === null
                  ? "warning"
                  : prediction.isCorrect
                  ? "success"
                  : "danger"
              } size="lg">
                {prediction.isCorrect === null
                  ? "Pending"
                  : prediction.isCorrect
                  ? "Correct"
                  : "Incorrect"}
              </Badge>
            </div>

            <div className="flex items-center justify-between py-2">
              <span className="text-[15px] text-[#5B6473] font-medium">Date</span>
              <span className="text-[15px] font-medium text-[#11131A]">
                {new Date(prediction.createdAt).toLocaleString()}
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}