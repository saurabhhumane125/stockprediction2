import * as React from "react";

import { cn } from "@/lib/cn";

export type LabelProps =
  React.LabelHTMLAttributes<HTMLLabelElement>;

export function Label({
  className,
  children,
  ...props
}: LabelProps) {
  return (
    <label
      className={cn(
        "mb-2 block text-sm font-semibold text-[#11131A]",
        className
      )}
      {...props}
    >
      {children}
    </label>
  );
}