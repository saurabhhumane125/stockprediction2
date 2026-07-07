import { ErrorState } from "@/components/feedback/ErrorState";

interface DashboardErrorProps {
  message: string;
}

export function DashboardError({
  message,
}: Readonly<DashboardErrorProps>) {
  return (
    <ErrorState
      message={message}
    />
  );
}