import * as React from "react";

import { cn } from "@/lib/cn";

export type ContainerProps = React.HTMLAttributes<HTMLDivElement>;

export function Container({

  className,

  children,

  ...props

}: ContainerProps) {

  return (

    <div

      className={cn(

        "mx-auto w-full max-w-[1440px] px-5 sm:px-6 lg:px-10 xl:px-12",

        className,

      )}

      {...props}

    >

      {children}

    </div>

  );

}