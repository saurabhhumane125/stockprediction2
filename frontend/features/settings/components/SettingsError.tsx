import {

  ErrorState,

} from "@/components/feedback/ErrorState";

interface SettingsErrorProps {

  message: string;

}

export function SettingsError({

  message,

}: Readonly<SettingsErrorProps>) {

  return (

    <ErrorState

      message={message}

    />

  );

}