import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
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

    <Card>

      <CardHeader>

        <CardTitle>

          Latest Prediction

        </CardTitle>

      </CardHeader>

      <CardContent>

        {!prediction && (

          <p>No prediction available.</p>

        )}

        {prediction && (

          <div className="space-y-4">

            <Badge

              variant={

                prediction.prediction === "BUY"

                  ? "buy"

                  : "sell"

              }

            >

              {prediction.prediction}

            </Badge>

            <div>

              Confidence:{" "}

              {(prediction.confidence * 100).toFixed(2)}%

            </div>

            <div>

              Result:{" "}

              {prediction.isCorrect === null

                ? "Pending"

                : prediction.isCorrect

                ? "Correct"

                : "Incorrect"}

            </div>

            <div>

              {new Date(

                prediction.createdAt,

              ).toLocaleString()}

            </div>

          </div>

        )}

      </CardContent>

    </Card>

  );

}