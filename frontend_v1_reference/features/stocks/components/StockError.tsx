import { ErrorState } from "@/components/feedback/ErrorState";

interface StockErrorProps {

  message: string;

}

export function StockError({

  message,

}: Readonly<StockErrorProps>) {

  return (

    <ErrorState

      message={message}

    />

  );

}