"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { Search, TrendingUp, AlertCircle, ArrowRight, Loader2 } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { useStocks } from "@/features/stocks/hooks/useStocks"

export default function StocksPage() {
  const router = useRouter()
  const { data: stocks, loading, error, predictingState, runPrediction } = useStocks()
  const [search, setSearch] = React.useState("")

  const filteredStocks = stocks.filter(s => 
    s.symbol.toLowerCase().includes(search.toLowerCase()) || 
    s.companyName.toLowerCase().includes(search.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex flex-col space-y-8">
        <Skeleton className="h-10 w-1/3" />
        <Skeleton className="h-10 w-full" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="h-32 w-full" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] space-y-4">
        <AlertCircle className="w-12 h-12 text-destructive" />
        <h2 className="text-xl font-semibold">Error Loading Stocks</h2>
        <p className="text-muted-foreground">{error}</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Markets & Assets</h1>
          <p className="text-muted-foreground mt-1">
            Browse available equities and trigger live AI predictions.
          </p>
        </div>
        <div className="relative w-full md:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input 
            placeholder="Search symbols..." 
            className="pl-9 bg-white shadow-sm"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredStocks.map((stock) => (
          <Card key={stock.id} className="hover:border-primary/50 transition-colors shadow-sm group">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{stock.symbol}</CardTitle>
                <div className="p-2 bg-primary/5 rounded-full text-primary">
                  <TrendingUp className="w-4 h-4" />
                </div>
              </div>
              <CardDescription className="line-clamp-1">{stock.companyName}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mt-2">
                <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-muted text-muted-foreground">
                  {stock.sector || "Equities"}
                </span>
                <div className="flex items-center gap-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    disabled={predictingState[stock.symbol]}
                    className="group-hover:bg-primary group-hover:text-primary-foreground transition-colors"
                    onClick={(e) => {
                      e.stopPropagation();
                      runPrediction(stock.symbol, () => {
                        router.push(`/dashboard?symbol=${stock.symbol}`);
                      });
                    }}
                  >
                    {predictingState[stock.symbol] ? <Loader2 className="w-4 h-4 animate-spin" /> : "Run Prediction"}
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="transition-colors"
                    onClick={() => router.push(`/dashboard?symbol=${stock.symbol}`)}
                  >
                    Dashboard <ArrowRight className="ml-2 w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {filteredStocks.length === 0 && (
        <div className="text-center py-12 text-muted-foreground">
          No stocks found matching "{search}"
        </div>
      )}
    </div>
  )
}
