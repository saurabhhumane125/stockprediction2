"use client";

import * as React from "react";

import { cn } from "@/lib/cn";

export type TextAreaProps =
  React.TextareaHTMLAttributes<HTMLTextAreaElement>;

export const TextArea = React.forwardRef<
  HTMLTextAreaElement,
  TextAreaProps
>(function TextArea(
  {
    className,
    ...props
  },
  ref
) {
  return (
    <textarea
      ref={ref}
      className={cn(
        "min-h-[120px] w-full rounded-xl border border-[#D8E0E8]",
        "bg-white p-4 text-[#11131A]",
        "placeholder:text-[#7A8394]",
        "transition-all duration-200",
        "focus:border-[#0066FF]",
        "focus:outline-none",
        "focus:ring-4 focus:ring-blue-100",
        "disabled:cursor-not-allowed",
        "disabled:opacity-60",
        className
      )}
      {...props}
    />
  );
});