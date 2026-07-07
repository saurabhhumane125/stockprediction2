import {
  TrendingUp,
  TrendingDown,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";

type WatchlistItem = {

  symbol: string;

  price: number;

  change: number;

};

type WatchlistCardProps = {

  items: WatchlistItem[];

};

export function WatchlistCard({

  items,

}: WatchlistCardProps) {

  return (

    <Card variant="elevated">

      <CardHeader>

        <CardTitle>

          Watchlist

        </CardTitle>

      </CardHeader>

      <CardContent className="space-y-4">

        {

          items.map((item)=>(

            <div
              key={item.symbol}
              className="flex items-center justify-between"
            >

              <div>

                <p className="font-semibold">

                  {item.symbol}

                </p>

                <p className="text-sm text-[#5B6473]">

                  ₹{item.price.toFixed(2)}

                </p>

              </div>

              <div
                className={`flex items-center gap-2 ${
                  item.change>=0
                  ? "text-green-600"
                  : "text-red-600"
                }`}
              >

                {

                  item.change>=0

                  ? <TrendingUp size={18}/>

                  : <TrendingDown size={18}/>

                }

                {item.change.toFixed(2)}%

              </div>

            </div>

          ))

        }

      </CardContent>

    </Card>

  );

}