import {

  Card,

  CardContent,

  CardHeader,

  CardTitle,

} from "@/components/ui/Card";

import { Badge } from "@/components/ui/Badge";

import type {

  HistoryItem,

} from "../types/history.view.types";

interface HistoryTableProps {

  history: HistoryItem[];

}

export function HistoryTable({

  history,

}: Readonly<HistoryTableProps>) {

  return (

    <Card>

      <CardHeader>

        <CardTitle>

          Prediction History

        </CardTitle>

      </CardHeader>

      <CardContent>

        <div className="overflow-x-auto">

          <table className="min-w-full">

            <thead>

              <tr className="border-b">

                <th className="py-3 text-left">
                  Stock
                </th>

                <th className="py-3 text-left">
                  Prediction
                </th>

                <th className="py-3 text-left">
                  Confidence
                </th>

                <th className="py-3 text-left">
                  Buy %
                </th>

                <th className="py-3 text-left">
                  Sell %
                </th>

                <th className="py-3 text-left">
                  Created
                </th>

              </tr>

            </thead>

            <tbody>

              {history.map((row) => (

                <tr
                  key={row.id}
                  className="border-b"
                >

                  <td className="py-4">

                    {row.symbol}

                  </td>

                  <td className="py-4">

                    <Badge
                      variant={
                        row.prediction === "BUY"
                          ? "buy"
                          : "sell"
                      }
                    >

                      {row.prediction}

                    </Badge>

                  </td>

                  <td className="py-4">

                    {(row.confidence * 100).toFixed(2)}%

                  </td>

                  <td className="py-4">

                    {row.probabilityBuy === null
                      ? "-"
                      : `${(row.probabilityBuy * 100).toFixed(2)}%`}

                  </td>

                  <td className="py-4">

                    {row.probabilitySell === null
                      ? "-"
                      : `${(row.probabilitySell * 100).toFixed(2)}%`}

                  </td>

                  <td className="py-4">

                    {new Date(
                      row.createdAt,
                    ).toLocaleString()}

                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      </CardContent>

    </Card>

  );

}