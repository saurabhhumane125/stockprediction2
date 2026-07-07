import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";

import type {
  BacktestingViewModel,
} from "../types/backtesting.view.types";

interface Props {

  data: BacktestingViewModel;

}

export function BacktestingSummaryCard({

  data,

}: Readonly<Props>) {

  const metrics = [

    {
      label: "Total",
      value: data.totalPredictions,
    },

    {
      label: "Evaluated",
      value: data.evaluatedPredictions,
    },

    {
      label: "Pending",
      value: data.pendingPredictions,
    },

    {
      label: "Wins",
      value: data.wins,
    },

    {
      label: "Losses",
      value: data.losses,
    },

    {
      label: "Accuracy",
      value: `${data.accuracy}%`,
    },

  ];

  return (

    <Card>

      <CardHeader>

        <CardTitle>

          Backtesting Summary

        </CardTitle>

      </CardHeader>

      <CardContent>

        <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">

          {metrics.map(

            (metric) => (

              <div
                key={metric.label}
                className="rounded-2xl bg-slate-50 p-4"
              >

                <p className="text-sm text-slate-500">

                  {metric.label}

                </p>

                <h3 className="mt-2 text-2xl font-bold">

                  {metric.value}

                </h3>

              </div>

            ),

          )}

        </div>

      </CardContent>

    </Card>

  );

}