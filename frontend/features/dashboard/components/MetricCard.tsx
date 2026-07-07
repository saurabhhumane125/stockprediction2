import {
  ArrowDownRight,
  ArrowUpRight,
  Minus,
  type LucideIcon,
} from "lucide-react";

import {
  Card,
  CardContent,
} from "@/components/ui/Card";

import { Badge } from "@/components/ui/Badge";

import { cn } from "@/lib/cn";

type Trend = "up" | "down" | "neutral";

interface MetricCardProps {

  title: string;

  value: string | number;

  icon?: LucideIcon;

  trend?: Trend;

  change?: number;

  className?: string;

}

export function MetricCard({

  title,

  value,

  icon: Icon,

  trend = "neutral",

  change,

  className,

}: MetricCardProps) {

  const TrendIcon =

    trend === "up"

      ? ArrowUpRight

      : trend === "down"

      ? ArrowDownRight

      : Minus;

  const badgeVariant =

    trend === "up"

      ? "buy"

      : trend === "down"

      ? "sell"

      : "neutral";

  return (

    <Card
      variant="elevated"
      className={cn(
        "h-full",
        className
      )}
    >

      <CardContent className="space-y-5">

        <div className="flex items-start justify-between">

          <div>

            <p className="text-sm text-[#5B6473]">

              {title}

            </p>

            <h3 className="mt-2 font-['Space_Grotesk'] text-3xl font-bold text-[#11131A]">

              {value}

            </h3>

          </div>

          {

            Icon && (

              <div className="rounded-2xl bg-[#EDF1F5] p-3">

                <Icon
                  size={24}
                  className="text-[#0066FF]"
                />

              </div>

            )

          }

        </div>

        {

          change !== undefined && (

            <div className="flex items-center gap-3">

              <Badge variant={badgeVariant}>

                <TrendIcon
                  size={14}
                />

              </Badge>

              <span className="text-sm text-[#5B6473]">

                {change}% vs last period

              </span>

            </div>

          )

        }

      </CardContent>

    </Card>

  );

}