import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

interface PageToolbarProps {

  children: ReactNode;

  className?: string;

}

export function PageToolbar({

  children,

  className,

}: PageToolbarProps) {

  return (

    <div

      className={cn(

        "mb-8 flex flex-wrap items-center gap-4",

        className,

      )}

    >

      {children}

    </div>

  );

}