import { EmptyState } from "@/components/feedback/EmptyState";

export function BacktestingEmpty() {

  return (

    <EmptyState

      title="No Backtesting Data"

      description="Run predictions before viewing backtesting results."

    />

  );

}