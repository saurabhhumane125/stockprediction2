import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

interface ContentGridProps {

  children: ReactNode;

  className?: string;

}

export function ContentGrid({

  children,

  className,

}: Readonly<ContentGridProps>) {

  return (

    <div

      className={cn(

        "grid grid-cols-12 gap-6 lg:gap-8",

        className,

      )}

    >

      {children}

    </div>

  );

}