import { Loader2 } from "lucide-react";

import { cn } from "@/lib/cn";

export interface SpinnerProps {

  className?: string;

}

export function Spinner({

  className,

}: SpinnerProps) {

  return (

    <Loader2

      className={cn(

        "h-5 w-5 animate-spin text-current",

        className,

      )}

    />

  );

}