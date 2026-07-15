"use client"

import * as React from "react"
import { History as HistoryIcon, TrendingUp, AlertCircle, Clock } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { useHistory } from "@/features/history/hooks/useHistory"
import { cn } from "@/lib/utils"

export default function HistoryPage() {
  const { data, loading, error } = useHistory()

  if (loading) {
    return (
      <div className="flex flex-col space-y-8">
        <Skeleton className="h-10 w-1/3" />
        <Skeleton className="h-[500px] w-full" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] space-y-4">
        <AlertCircle className="w-12 h-12 text-destructive" />
        <h2 className="text-xl font-semibold">Error Loading History</h2>
        <p className="text-muted-foreground">{error}</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Prediction Log</h1>
        <p className="text-muted-foreground mt-1">
          Historical record of all AI inferences and model performance.
        </p>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <div className="flex items-center gap-2">
            <HistoryIcon className="w-5 h-5 text-primary" />
            <CardTitle>Inference Ledger</CardTitle>
          </div>
          <CardDescription>Comprehensive timeline of predictive analytics</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>Time</TableHead>
                <TableHead>Asset</TableHead>
                <TableHead>Forecast</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead className="text-right">Probabilities (Buy / Sell)</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.history.map((record) => (
                <TableRow key={record.id} className="group">
                  <TableCell>
                    <div className="flex items-center gap-2 text-muted-foreground whitespace-nowrap">
                      <Clock className="w-3 h-3" />
                      {new Date(record.createdAt).toLocaleString()}
                    </div>
                  </TableCell>
                  <TableCell className="font-semibold text-foreground">
                    {record.symbol}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <TrendingUp className={cn(
                        "w-4 h-4",
                        record.prediction === "UP" ? "text-emerald-500" : "text-destructive rotate-180"
                      )} />
                      <span className={cn(
                        "font-medium",
                        record.prediction === "UP" ? "text-emerald-600" : "text-destructive"
                      )}>
                        {record.prediction}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary" className="bg-muted">
                      {(record.confidence).toFixed(2)}%
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2 text-sm">
                      <span className="text-emerald-600 font-medium">
                        {((record.probabilityBuy || 0) * 100).toFixed(1)}%
                      </span>
                      <span className="text-muted-foreground">/</span>
                      <span className="text-destructive font-medium">
                        {((record.probabilitySell || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {data.history.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center text-muted-foreground">
                    No prediction history found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
