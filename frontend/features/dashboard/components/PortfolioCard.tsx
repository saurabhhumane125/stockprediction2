import {
  Wallet,
  TrendingUp,
} from "lucide-react";

import { Button } from "@/components/ui/Button";

import { MetricCard } from "./MetricCard";

type PortfolioCardProps = {

  totalValue: number;

  dailyChange: number;

  totalReturn: number;

  onViewPortfolio?: () => void;

};

export function PortfolioCard({

  totalValue,

  dailyChange,

  totalReturn,

  onViewPortfolio,

}: PortfolioCardProps) {

  return (

    <div className="space-y-4">

      <MetricCard
        title="Portfolio Value"
        value={`₹${totalValue.toLocaleString()}`}
        icon={Wallet}
        trend={
          dailyChange >= 0
            ? "up"
            : "down"
        }
        change={Math.abs(dailyChange)}
      />

      <MetricCard
        title="Overall Return"
        value={`${totalReturn.toFixed(2)}%`}
        icon={TrendingUp}
        trend={
          totalReturn >= 0
            ? "up"
            : "down"
        }
        change={Math.abs(totalReturn)}
      />

      <Button
        fullWidth
        onClick={onViewPortfolio}
      >
        View Portfolio
      </Button>

    </div>

  );

}