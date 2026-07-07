import { EmptyState } from "@/components/feedback/EmptyState";

export function PredictionEmpty() {
  return (
    <EmptyState
      title="No Prediction Available"
      description="Choose a stock and generate a live prediction."
    />
  );
}