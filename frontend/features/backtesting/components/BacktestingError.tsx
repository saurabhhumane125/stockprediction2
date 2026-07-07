import { ErrorState } from "@/components/feedback/ErrorState";

interface BacktestingErrorProps {

  message: string;

}

export function BacktestingError({

  message,

}: Readonly<BacktestingErrorProps>) {

  return (

    <ErrorState

      message={message}

    />

  );

}