"use client";

import * as React from "react";

import { cn } from "@/lib/cn";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<
  HTMLInputElement,
  InputProps
>(function Input(
  {
    className,
    type = "text",
    ...props
  },
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
          "rounded-2xl",
          "border",
          "border-[#D7DEE7]",
          "bg-white",
          "px-4",
          "text-[15px]",
          "font-medium",
          "text-[#11131A]",
          "placeholder:text-[#7A8496]",
          "transition-all",
          "duration-300",
          "outline-none",
          "shadow-sm",
          "hover:border-[#BFC8D6]",
          "hover:shadow-md",
          "focus:border-[#0066FF]",
          "focus:ring-4",
          "focus:ring-[#0066FF]/15",
          "disabled:cursor-not-allowed",
          "disabled:opacity-60",
          "disabled:bg-[#F7F9FC]",
          "autofill:bg-white",
        ].join(" "),

        className,

      )}

      {...props}

    />

  );

});

Input.displayName = "Input";

export { Input };