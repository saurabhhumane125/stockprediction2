//import { cn } from "@/lib/cn";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/Card";

type ConfidenceGaugeProps = {

  value: number;

  className?: string;

};

export function ConfidenceGauge({

  value,

  className,

}: ConfidenceGaugeProps) {

  const percentage = Math.min(
    100,
    Math.max(0, value)
  );

  const color =

    percentage >= 80
      ? "#16A34A"
      : percentage >= 60
      ? "#0066FF"
      : percentage >= 40
      ? "#F59E0B"
      : "#FF3B3B";

  return (

    <Card
      variant="elevated"
      className={className}
    >

      <CardHeader>

        <CardTitle>

          Prediction Confidence

        </CardTitle>

        <CardDescription>

          Model confidence score

        </CardDescription>

      </CardHeader>

      <CardContent>

        <div className="flex flex-col items-center gap-6">

          <div
            className="relative flex h-44 w-44 items-center justify-center rounded-full"
            style={{
              background: `conic-gradient(${color} ${percentage * 3.6}deg,#E5E7EB 0deg)`,
            }}
          >

            <div className="flex h-32 w-32 items-center justify-center rounded-full bg-white">

              <span className="font-['Space_Grotesk'] text-4xl font-bold text-[#11131A]">

                {percentage.toFixed(0)}%

              </span>

            </div>

          </div>

          <div className="w-full">

            <div className="mb-2 flex justify-between text-sm text-[#5B6473]">

              <span>Low</span>

              <span>High</span>

            </div>

            <div className="h-3 overflow-hidden rounded-full bg-[#E5E7EB]">

              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${percentage}%`,
                  backgroundColor: color,
                }}
              />

            </div>

          </div>

        </div>

      </CardContent>

    </Card>

  );

}