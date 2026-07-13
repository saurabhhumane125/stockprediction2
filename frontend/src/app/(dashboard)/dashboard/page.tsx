"use client"

import * as React from "react"
import { BarChart3, TrendingUp, Activity, CheckCircle2, AlertCircle } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

import { useSearchParams } from "next/navigation"
import { useDashboard } from "@/features/dashboard/hooks/useDashboard"

function DashboardContent() {
  const searchParams = useSearchParams()
  const symbol = searchParams.get("symbol") || "RELIANCE"


  const { data, loading, error } = useDashboard(symbol)

  if (loading) {
    return (
      <div className="flex flex-col space-y-8">
        <div className="space-y-2">
          <Skeleton className="h-10 w-1/3" />
          <Skeleton className="h-4 w-1/4" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32 w-full" />
          ))}
        </div>
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] space-y-4">
        <AlertCircle className="w-12 h-12 text-destructive" />
        <h2 className="text-xl font-semibold">Error Loading Dashboard</h2>
        <p className="text-muted-foreground">{error}</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            {data.stock.companyName} ({data.stock.symbol}) Overview
          </h1>
          <p className="text-muted-foreground mt-1">
            Real-time market insights and AI-driven predictions.
          </p>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="hover:border-ring/20 transition-all duration-300 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Latest Price
            </CardTitle>
            <Activity className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{data.latestPrice?.price?.toFixed(2) || "N/A"}
            </div>
            {data.latestPrice && (
              <p className={cn(
                "text-xs mt-1 font-medium",
                data.latestPrice.price >= data.latestPrice.open ? "text-emerald-600" : "text-destructive"
              )}>
                {data.latestPrice.price >= data.latestPrice.open ? "+" : ""}
                {((data.latestPrice.price - data.latestPrice.open) / data.latestPrice.open * 100).toFixed(2)}% today
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="hover:border-ring/20 transition-all duration-300 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              AI Recommendation
            </CardTitle>
            <CheckCircle2 className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {data.recommendation?.action || "NEUTRAL"}
            </div>
            <div className="flex flex-col mt-1 gap-1">
              <p className="text-xs font-medium text-emerald-600">
                {data.recommendation?.strength || "Moderate"} Signal
              </p>
              {data.recommendation?.reason && (
                <p className="text-xs text-muted-foreground line-clamp-1" title={data.recommendation.reason}>
                  {data.recommendation.reason}
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-ring/20 transition-all duration-300 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Prediction Confidence
            </CardTitle>
            <BarChart3 className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(data.recommendation?.confidence || 0).toFixed(1)}%
            </div>
            <p className="text-xs mt-1 font-medium text-muted-foreground">
              Based on deep learning ensemble
            </p>
          </CardContent>
        </Card>

        <Card className="hover:border-ring/20 transition-all duration-300 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Volume
            </CardTitle>
            <TrendingUp className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(data.latestPrice?.volume || 0).toLocaleString()}
            </div>
            <p className="text-xs mt-1 font-medium text-muted-foreground">
              Traded today
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        <Card className="lg:col-span-4 flex flex-col shadow-sm">
          <CardHeader>
            <CardTitle>Technical Analysis</CardTitle>
            <CardDescription>
              Detailed breakdown of the current technical and news signals.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Technical Indicators */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-foreground border-b pb-2">Technical Indicators</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {[
                  { label: "Trend", value: data.prediction?.explanation?.trend },
                  { label: "Trend Strength", value: data.prediction?.explanation?.trendStrength },
                  { label: "RSI", value: data.prediction?.explanation?.rsi?.toFixed(2) },
                  { label: "RSI State", value: data.prediction?.explanation?.rsiState },
                  { label: "ROC", value: data.prediction?.explanation?.roc?.toFixed(2) },
                  { label: "Momentum", value: data.prediction?.explanation?.momentum?.toFixed(2) },
                  { label: "ATR", value: data.prediction?.explanation?.atr?.toFixed(2) },
                  { label: "Volatility", value: data.prediction?.explanation?.volatility?.toFixed(2) },
                  { label: "Bollinger Width", value: data.prediction?.explanation?.bollingerWidth?.toFixed(2) },
                  { label: "Price Position", value: data.prediction?.explanation?.pricePosition },
                  { label: "Volume Trend", value: data.prediction?.explanation?.volumeTrend }
                ].map((indicator, idx) => (
                  <div key={idx} className="flex flex-col space-y-1 bg-muted/30 p-2 rounded-md border border-border/50">
                    <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">{indicator.label}</span>
                    <span className="text-sm font-semibold">{indicator.value || "N/A"}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Latest Market Candle */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-foreground border-b pb-2">Latest Market Candle</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                {[
                  { label: "Date", value: data.prediction?.latestCandle?.date },
                  { label: "Open", value: data.prediction?.latestCandle?.open?.toFixed(2) },
                  { label: "High", value: data.prediction?.latestCandle?.high?.toFixed(2) },
                  { label: "Low", value: data.prediction?.latestCandle?.low?.toFixed(2) },
                  { label: "Close", value: data.prediction?.latestCandle?.close?.toFixed(2) },
                  { label: "Volume", value: data.prediction?.latestCandle?.volume?.toLocaleString() }
                ].map((candleData, idx) => (
                  <div key={idx} className="flex flex-col space-y-1 bg-muted/30 p-2 rounded-md border border-border/50">
                    <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">{candleData.label}</span>
                    <span className="text-sm font-semibold">{candleData.value || "N/A"}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Explanation Summary */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-foreground border-b pb-2">AI Summary</h4>
              <div className="space-y-2 text-sm text-muted-foreground bg-muted/30 p-4 rounded-md border border-border/50">
                {data.prediction?.explanation?.summary?.length ? (
                  <ul className="list-disc list-inside space-y-1">
                    {data.prediction.explanation.summary.map((sentence, i) => (
                      <li key={i}>{sentence}</li>
                    ))}
                  </ul>
                ) : (
                  <p>No explanation summary available.</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-3 flex flex-col shadow-sm">
          <CardHeader>
            <CardTitle>Latest Prediction</CardTitle>
            <CardDescription>
              Most recent model inference results.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 overflow-auto">
            {data.prediction ? (
              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 rounded-lg bg-muted/30 border border-border/50">
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-muted-foreground">Forecast</p>
                    <p className={cn(
                      "text-2xl font-bold",
                      data.prediction.prediction === "UP" ? "text-emerald-600" : "text-destructive"
                    )}>
                      {data.prediction.prediction}
                    </p>
                  </div>
                  <Badge variant="outline" className="text-sm px-3 py-1 bg-background">
                    {data.prediction.confidence.toFixed(1)}% Conf.
                  </Badge>
                </div>

                <div className="space-y-4 pt-2">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Buy Probability</span>
                      <span className="font-medium text-emerald-600">
                        {((data.prediction.probabilityBuy || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className="bg-emerald-500 h-2 rounded-full"
                        style={{ width: `${(data.prediction.probabilityBuy || 0) * 100}%` }}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Sell Probability</span>
                      <span className="font-medium text-destructive">
                        {((data.prediction.probabilitySell || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className="bg-destructive h-2 rounded-full"
                        style={{ width: `${(data.prediction.probabilitySell || 0) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-4 border-t border-border/50">
                  <div className="space-y-1 bg-muted/20 p-2 rounded-md">
                    <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">Technical Signal</span>
                    <div className="text-sm font-semibold">{data.prediction.technicalSignal || "Neutral"}</div>
                  </div>
                  <div className="space-y-1 bg-muted/20 p-2 rounded-md">
                    <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">News Signal</span>
                    <div className="text-sm font-semibold">{data.prediction.newsSignal || "Neutral"}</div>
                  </div>
                </div>

                <div className="space-y-2 pt-2">
                  <h4 className="text-xs font-semibold text-foreground uppercase tracking-wider">Recommendation Reason</h4>
                  <p className="text-sm text-muted-foreground bg-muted/30 p-3 rounded-md border border-border/50">
                    {data.prediction.finalReason || "No detailed reason available at this time."}
                  </p>
                </div>

                {/* Market Regime Block */}
                {data.prediction.marketRegime && (
                  <div className="space-y-3 pt-4 border-t border-border/50">
                    <h4 className="text-xs font-semibold text-foreground uppercase tracking-wider">Market Regime Context</h4>
                    <div className="bg-muted/30 p-3 rounded-md border border-border/50 flex flex-col space-y-1">
                      <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">Regime</span>
                      <span className="text-sm font-semibold">{data.prediction.marketRegime.regime || "N/A"}</span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
                No active predictions found.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <React.Suspense fallback={<Skeleton className="w-full h-screen" />}>
      <DashboardContent />
    </React.Suspense>
  )
}
