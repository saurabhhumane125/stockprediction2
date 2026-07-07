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
    "transition-all duration-300",
    "select-none",
    "active:scale-[0.98]",
    "disabled:pointer-events-none",
    "disabled:opacity-60",
    "focus-visible:outline-none",
    "focus-visible:ring-4",
    "focus-visible:ring-[#0066FF]/20",
  ].join(" "),

  {

    variants: {

      variant: {

        primary:

          [
            "bg-[#0066FF]",
            "text-white",
            "shadow-lg shadow-blue-500/20",
            "hover:-translate-y-0.5",
            "hover:bg-[#0057DB]",
            "hover:shadow-xl",
          ].join(" "),

        secondary:

          [
            "bg-[#B4FF00]",
            "text-[#11131A]",
            "shadow-lg",
            "hover:-translate-y-0.5",
            "hover:bg-[#C3D809]",
          ].join(" "),

        outline:

          [
            "border",
            "border-[#D7DEE7]",
            "bg-white",
            "text-[#11131A]",
            "hover:border-[#0066FF]",
            "hover:bg-[#EDF1F5]",
          ].join(" "),

        ghost:

          [
            "bg-transparent",
            "text-[#11131A]",
            "hover:bg-[#EDF1F5]",
          ].join(" "),

        danger:

          [
            "bg-[#FF3B3B]",
            "text-white",
            "hover:bg-[#E22E2E]",
          ].join(" "),

      },

      size: {

        sm:

          "h-10 rounded-xl px-4 text-sm",

        md:

          "h-12 rounded-2xl px-6 text-[15px]",

        lg:

          "h-14 rounded-2xl px-8 text-base",

        icon:

          "h-12 w-12 rounded-2xl",

      },

      fullWidth: {

        true:

          "w-full",

        false:

          "",

      },

    },

    defaultVariants: {

      variant:

        "primary",

      size:

        "md",

      fullWidth:

        false,

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

        buttonVariants({

          variant,

          size,

          fullWidth,

        }),

        className,

      )}

      disabled={disabled || loading}

      {...props}

    >

      {loading && (

        <Spinner className="h-4 w-4" />

      )}

      <span
        className={cn(
          loading && "opacity-70",
        )}
      >

        {children}

      </span>

    </Component>

  );

}

export { buttonVariants };