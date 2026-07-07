import {
  Activity,
  Clock4,
} from "lucide-react";

import {
  Card,
  CardContent,
} from "@/components/ui/Card";

import { Badge } from "@/components/ui/Badge";

interface Props {

  marketOpen: boolean;

  lastUpdated: string;

}

export function MarketStatusCard({

  marketOpen,

  lastUpdated,

}: Props) {

  return (

    <Card
      variant="elevated"
      className="h-full"
    >

      <CardContent className="space-y-8">

        <div className="flex items-start justify-between">

          <div>

            <p className="text-sm font-medium text-[#5B6473]">

              NSE Market

            </p>

            <h2 className="mt-2 text-3xl font-bold text-[#11131A]">

              {

                marketOpen

                  ? "Open"

                  : "Closed"

              }

            </h2>

          </div>

          <div
            className="
              rounded-2xl
              bg-[#EDF1F5]
              p-4
            "
          >

            <Activity
              size={28}
              className="text-[#0066FF]"
            />

          </div>

        </div>

        <Badge

          variant={

            marketOpen

              ? "buy"

              : "neutral"

          }

          size="lg"

        >

          {

            marketOpen

              ? "LIVE MARKET"

              : "MARKET CLOSED"

          }

        </Badge>

        <div
          className="
            flex
            items-center
            gap-3
            rounded-2xl
            bg-[#EDF1F5]
            p-4
          "
        >

          <Clock4
            size={18}
            className="text-[#0066FF]"
          />

          <div>

            <p className="text-xs text-[#5B6473]">

              Last Updated

            </p>

            <p className="font-semibold text-[#11131A]">

              {lastUpdated}

            </p>

          </div>

        </div>

      </CardContent>

    </Card>

  );

}