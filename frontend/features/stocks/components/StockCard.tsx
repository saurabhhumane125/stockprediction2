import {

  Card,

  CardContent,

  CardHeader,

  CardTitle,

} from "@/components/ui/Card";

import { Badge } from "@/components/ui/Badge";

import type {

  StockViewModel,

} from "../types/stock.view.types";

interface StockCardProps {

  stock: StockViewModel;

}

export function StockCard({

  stock,

}: Readonly<StockCardProps>) {

  return (

    <Card>

      <CardHeader>

        <CardTitle>

          {stock.symbol}

        </CardTitle>

      </CardHeader>

      <CardContent className="space-y-3">

        <div>

          <p className="text-sm text-slate-500">

            Company

          </p>

          <p className="font-medium">

            {stock.companyName}

          </p>

        </div>

        <div>

          <Badge variant="neutral">

            {stock.sector ?? "Unknown"}

          </Badge>

        </div>

      </CardContent>

    </Card>

  );

}