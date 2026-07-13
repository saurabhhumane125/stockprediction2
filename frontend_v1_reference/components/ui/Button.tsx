"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/cn";
import { Spinner } from "./Spinner";

const buttonVariants = cva(
  [
    "inline-flex items-center justify-center gap-2",
    "whitespace-nowrap",
    "font-semibold",
    "rounded-[10px]",
    "transition-all duration-150",
    "shrink-0",
    "select-none",
    "active:scale-[0.98]",
    "disabled:pointer-events-none",
    "disabled:opacity-50",
    "focus-visible:outline-none",
    "focus-visible:ring-2",
    "focus-visible:ring-[#0066FF]/20",
    "focus-visible:ring-offset-1",
  ].join(" "),
  {
    variants: {
      variant: {
        primary: [
          "bg-[#0066FF]",
          "text-white",
          "shadow-[0_1px_3px_rgba(0,102,255,0.2)]",
          "hover:bg-[#0055D4]",
          "hover:shadow-[0_2px_8px_rgba(0,102,255,0.25)]",
        ].join(" "),

        secondary: [
          "bg-[#B4FF00]",
          "text-[#11131A]",
          "shadow-[0_1px_3px_rgba(180,255,0,0.15)]",
          "hover:bg-[#A8EE00]",
        ].join(" "),

        outline: [
          "border border-[#E8EDF2]",
          "bg-white",
          "text-[#11131A]",
          "shadow-[0_1px_2px_rgba(17,19,26,0.04)]",
          "hover:bg-[#F7F9FC]",
          "hover:border-[#D7DEE7]",
        ].join(" "),

        ghost: [
          "bg-transparent",
          "text-[#5B6473]",
          "hover:bg-[#F0F4F8]",
          "hover:text-[#11131A]",
        ].join(" "),

        danger: [
          "bg-[#FF3B3B]",
          "text-white",
          "shadow-[0_1px_3px_rgba(255,59,59,0.2)]",
          "hover:bg-[#E83333]",
        ].join(" "),
      },

      size: {
        sm: "h-9 px-4 text-sm",
        md: "h-11 px-5 text-[15px]",
        lg: "h-12 px-6 text-base",
        icon: "h-11 w-11",
        "icon-sm": "h-9 w-9",
      },

      fullWidth: {
        true: "w-full",
        false: "",
      },
    },

    defaultVariants: {
      variant: "primary",
      size: "md",
      fullWidth: false,
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

export function Button({
  className,
  variant,
  size,
  fullWidth,
  asChild,
  loading,
  disabled,
  children,
  ...props
}: ButtonProps) {
  const Component = asChild ? Slot : "button";

  return (
    <Component
      className={cn(
        buttonVariants({ variant, size, fullWidth }),
        className,
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Spinner className="h-4 w-4" />}
      <span className={cn(loading && "opacity-70", "flex items-center gap-2")}>
        {children}
      </span>
    </Component>
  );
}

export { buttonVariants };