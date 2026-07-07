import { ErrorState } from "@/components/feedback/ErrorState";

interface PredictionErrorProps {
  message: string;
}

export function PredictionError({
  message,
}: Readonly<PredictionErrorProps>) {
  return (
    <ErrorState
      message={message}
    />
  );
}