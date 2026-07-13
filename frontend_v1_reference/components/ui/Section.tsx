import * as React from "react";

import { cn } from "@/lib/cn";

export type SectionProps = React.HTMLAttributes<HTMLElement>;

export function Section({

  className,

  children,

  ...props

}: SectionProps) {

  return (

    <section

      className={cn(

        "py-8 lg:py-12",

        className,

      )}

      {...props}

    >

      {children}

    </section>

  );

}