import { ErrorState } from "@/components/feedback/ErrorState";

interface HistoryErrorProps {

  message: string;

}

export function HistoryError({

  message,

}: Readonly<HistoryErrorProps>) {

  return (

    <ErrorState

      message={message}

    />

  );

}