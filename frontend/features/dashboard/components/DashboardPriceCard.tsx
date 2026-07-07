import {

  TrendingUp,

} from "lucide-react";

import {

  Card,

  CardContent,

} from "@/components/ui/Card";

import type {

  LatestPriceViewModel,

} from "../types/dashboard.view.types";

interface Props {

  price: LatestPriceViewModel;

}

export function DashboardPriceCard({

  price,

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

              Latest Price

            </p>

            <h2 className="mt-2 text-4xl font-bold text-[#11131A]">

              ₹{price.price.toFixed(2)}

            </h2>

          </div>

          <div
            className="
              rounded-2xl
              bg-[#EDF1F5]
              p-4
            "
          >

            <TrendingUp
              size={28}
              className="text-[#0066FF]"
            />

          </div>

        </div>

        <div className="grid grid-cols-2 gap-6">

          <div>

            <p className="text-sm text-[#5B6473]">

              Open

            </p>

            <p className="mt-1 font-semibold">

              ₹{price.open.toFixed(2)}

            </p>

          </div>

          <div>

            <p className="text-sm text-[#5B6473]">

              High

            </p>

            <p className="mt-1 font-semibold">

              ₹{price.high.toFixed(2)}

            </p>

          </div>

          <div>

            <p className="text-sm text-[#5B6473]">

              Low

            </p>

            <p className="mt-1 font-semibold">

              ₹{price.low.toFixed(2)}

            </p>

          </div>

          <div>

            <p className="text-sm text-[#5B6473]">

              Volume

            </p>

            <p className="mt-1 font-semibold">

              {price.volume.toLocaleString()}

            </p>

          </div>

        </div>

      </CardContent>

    </Card>

  );

}