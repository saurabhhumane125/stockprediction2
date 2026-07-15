"use client"

import * as React from "react"
import { Search, Activity, Target, ArrowRight, ShieldCheck, AlertCircle } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { useBacktesting } from "@/features/backtesting/hooks/useBacktesting"
import { cn } from "@/lib/utils"

export default function BacktestingPage() {
  const [symbol, setSymbol] = React.useState("RELIANCE")
  const [searchQuery, setSearchQuery] = React.useState("RELIANCE")
  const { data, loading, error } = useBacktesting(symbol)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      setSymbol(searchQuery.toUpperCase())
    }
  }

  return (
    <div className="flex flex-col space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Strategy Backtesting</h1>
          <p className="text-muted-foreground mt-1">
            Evaluate historical performance and model accuracy by asset.
          </p>
        </div>
        <form onSubmit={handleSearch} className="relative w-full md:w-80 flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input 
              placeholder="Enter stock symbol (e.g., AAPL)" 
              className="pl-9 bg-white shadow-sm"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Button type="submit" variant="secondary" className="shadow-sm">Analyze</Button>
        </form>
      </div>

      {loading ? (
        <div className="space-y-6">
          <Skeleton className="h-10 w-48" />
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-32 w-full" />
            ))}
          </div>
          <Skeleton className="h-64 w-full" />
        </div>
      ) : error || !data ? (
        <div className="flex flex-col items-center justify-center h-[50vh] space-y-4">
          <AlertCircle className="w-12 h-12 text-destructive" />
          <h2 className="text-xl font-semibold">Simulation Error</h2>
          <p className="text-muted-foreground">{error || "No data available."}</p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <Badge variant="outline" className="text-sm px-3 py-1 bg-white">
              {data.stock}
            </Badge>
            <span className="text-sm text-muted-foreground flex items-center gap-1">
              <ShieldCheck className="w-4 h-4" /> Validated Model
            </span>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card className="shadow-sm">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Accuracy</CardTitle>
                <Target className="w-4 h-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{(data.accuracy).toFixed(1)}%</div>
              </CardContent>
            </Card>

            <Card className="shadow-sm">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Win Rate</CardTitle>
                <Activity className="w-4 h-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-emerald-600">{(data.winRate).toFixed(1)}%</div>
                <p className="text-xs text-muted-foreground mt-1">{data.wins} successful trades</p>
              </CardContent>
            </Card>

            <Card className="shadow-sm">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Loss Rate</CardTitle>
                <AlertCircle className="w-4 h-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-destructive">{(data.lossRate).toFixed(1)}%</div>
                <p className="text-xs text-muted-foreground mt-1">{data.losses} failed trades</p>
              </CardContent>
            </Card>

            <Card className="shadow-sm">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Avg Confidence</CardTitle>
                <ArrowRight className="w-4 h-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{(data.averageConfidence).toFixed(2)}%</div>
              </CardContent>
            </Card>
          </div>

          <Card className="shadow-sm">
            <CardHeader>
              <CardTitle>Simulation Metrics</CardTitle>
              <CardDescription>Evaluation data over {data.totalPredictions} total predictions.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center py-3 border-b border-border/50">
                  <span className="text-sm text-muted-foreground">Evaluated Predictions</span>
                  <span className="font-semibold">{data.evaluatedPredictions}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-border/50">
                  <span className="text-sm text-muted-foreground">Pending Resolution</span>
                  <span className="font-semibold text-amber-600">{data.pendingPredictions}</span>
                </div>
                {data.latestPrediction && (
                  <div className="pt-4">
                    <h4 className="text-sm font-medium mb-3">Latest Backtest State</h4>
                    <div className="p-4 bg-muted/30 rounded-lg border border-border/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div>
                        <span className="text-xs text-muted-foreground uppercase tracking-wider block mb-1">Prediction</span>
                        <span className={cn(
                          "font-bold",
                          data.latestPrediction.prediction === "UP" ? "text-emerald-600" : "text-destructive"
                        )}>{data.latestPrediction.prediction}</span>
                      </div>
                      <div>
                        <span className="text-xs text-muted-foreground uppercase tracking-wider block mb-1">Confidence</span>
                        <span className="font-medium">{data.latestPrediction.confidence.toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-xs text-muted-foreground uppercase tracking-wider block mb-1">Status</span>
                        <Badge variant={data.latestPrediction.isCorrect === true ? "default" : data.latestPrediction.isCorrect === false ? "destructive" : "secondary"}
                               className={data.latestPrediction.isCorrect === true ? "bg-emerald-500 hover:bg-emerald-600" : ""}>
                          {data.latestPrediction.isCorrect === true ? "Correct" : data.latestPrediction.isCorrect === false ? "Incorrect" : "Pending"}
                        </Badge>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
