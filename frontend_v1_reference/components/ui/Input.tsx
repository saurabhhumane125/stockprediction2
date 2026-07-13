"use client";

import * as React from "react";
import { cn } from "@/lib/cn";

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

const Input = React.forwardRef<HTMLInputElement, InputProps>(function Input(
  { className, type = "text", ...props },
  ref,
) {
  return (
    <input
      ref={ref}
      type={type}
      className={cn(
        [
          "flex",
          "h-12",
          "w-full",
          "rounded-[10px]",
          "border border-[#E8EDF2]",
          "bg-[#F7F9FC]",
          "px-4",
          "text-base",
          "font-medium",
          "text-[#11131A]",
          "placeholder:text-[#8B95A5]",
          "placeholder:font-normal",
          "transition-all duration-150 ease-[cubic-bezier(0.16,1,0.3,1)]",
          "outline-none",
          "shadow-[0_1px_2px_rgba(17,19,26,0.02)_inset]",
          "hover:border-[#D7DEE7]",
          "focus:border-[#0066FF]",
          "focus:bg-white",
          "focus:shadow-[0_1px_2px_rgba(17,19,26,0.04)]",
          "focus:ring-[3px]",
          "focus:ring-[#0066FF]/10",
          "disabled:cursor-not-allowed",
          "disabled:opacity-50",
          "disabled:bg-[#EDF1F5]",
        ].join(" "),
        className,
      )}
      {...props}
    />
  );
});

Input.displayName = "Input";

export { Input };