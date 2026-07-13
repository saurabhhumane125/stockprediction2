import {
  BrainCircuit,
  TrendingDown,
  TrendingUp,
  Minus,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/Card";

import { Badge } from "@/components/ui/Badge";

type Prediction = "BUY" | "SELL" | "HOLD";

interface PredictionCardProps {

  stock: string;

  prediction: Prediction;

  confidence: number;

  targetPrice?: number;

}

export function PredictionCard({

  stock,

  prediction,

  confidence,

  targetPrice,

}: PredictionCardProps) {

  const Icon =

    prediction === "BUY"

      ? TrendingUp

      : prediction === "SELL"

      ? TrendingDown

      : Minus;

  const badgeVariant =

    prediction === "BUY"

      ? "buy"

      : prediction === "SELL"

      ? "sell"

      : "neutral";

  return (

    <Card variant="elevated">

      <CardHeader>

        <div>

          <CardTitle>

            {stock}

          </CardTitle>

          <CardDescription>

            AI Prediction

          </CardDescription>

        </div>

        <BrainCircuit
          size={26}
          className="text-[#0066FF]"
        />

      </CardHeader>

      <CardContent className="space-y-5">

        <Badge
          variant={badgeVariant}
          size="lg"
        >

          <Icon size={16} />

          <span className="ml-2">

            {prediction}

          </span>

        </Badge>

        <div>

          <p className="text-sm text-[#5B6473]">

            Confidence

          </p>

          <p className="mt-1 text-3xl font-bold text-[#11131A]">

            {confidence.toFixed(1)}%

          </p>

        </div>

        {

          targetPrice !== undefined && (

            <div>

              <p className="text-sm text-[#5B6473]">

                Target Price

              </p>

              <p className="mt-1 text-xl font-semibold">

                ₹{targetPrice.toFixed(2)}

              </p>

            </div>

          )

        }

      </CardContent>

    </Card>

  );

}