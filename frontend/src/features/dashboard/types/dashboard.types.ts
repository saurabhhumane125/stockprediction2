import { LucideIcon } from "lucide-react";

export interface MetricCardData {
  title: string;
  value: string | number;
  change?: number;
  trend?: "up" | "down" | "neutral";
  icon?: LucideIcon;
}

export interface ChartCardData {
  title: string;
  subtitle?: string;
}

export interface PredictionData {
  stock: string;
  prediction: "BUY" | "SELL" | "HOLD";
  confidence: number;
}

export interface MarketStatusData {
  status: "OPEN" | "CLOSED";
  nextUpdate: string;
}

export interface NewsItem {
  id: string;
  title: string;
  source: string;
  publishedAt: string;
}