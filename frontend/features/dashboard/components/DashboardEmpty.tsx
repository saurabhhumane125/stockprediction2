import { EmptyState } from "@/components/feedback/EmptyState";

export function DashboardEmpty() {
  return (
    <EmptyState
      title="No Dashboard Data"
      description="No dashboard information is available for the selected stock."
    />
  );
}