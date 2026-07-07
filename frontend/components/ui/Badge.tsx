import * as React from "react";

import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/cn";

const badgeVariants = cva(

  [
    "inline-flex",
    "items-center",
    "justify-center",
    "rounded-full",
    "border",
    "px-3",
    "py-1",
    "text-xs",
    "font-semibold",
    "tracking-wide",
    "transition-all",
    "duration-300",
    "select-none",
  ].join(" "),

  {

    variants: {

      variant: {

        primary:

          [
            "border-transparent",
            "bg-[#0066FF]",
            "text-white",
            "shadow-sm",
            "shadow-blue-500/20",
          ].join(" "),

        accent:

          [
            "border-transparent",
            "bg-[#B4FF00]",
            "text-[#11131A]",
          ].join(" "),

        secondary:

          [
            "border-transparent",
            "bg-[#C3D809]",
            "text-[#11131A]",
          ].join(" "),

        success:

          [
            "border-transparent",
            "bg-[#B4FF00]",
            "text-[#11131A]",
          ].join(" "),

        warning:

          [
            "border-transparent",
            "bg-[#FFF3D6]",
            "text-[#11131A]",
          ].join(" "),

        danger:

          [
            "border-transparent",
            "bg-[#FF3B3B]",
            "text-white",
          ].join(" "),

        outline:

          [
            "border-[#D7DEE7]",
            "bg-white",
            "text-[#11131A]",
          ].join(" "),

        neutral:

          [
            "border-transparent",
            "bg-[#EDF1F5]",
            "text-[#5B6473]",
          ].join(" "),

        buy:

          [
            "border-transparent",
            "bg-[#B4FF00]",
            "text-[#11131A]",
          ].join(" "),

        sell:

          [
            "border-transparent",
            "bg-[#FF3B3B]",
            "text-white",
          ].join(" "),

      },

      size: {

        sm:

          "px-2.5 py-1 text-[11px]",

        md:

          "px-3 py-1.5 text-xs",

        lg:

          "px-4 py-2 text-sm",

      },

    },

    defaultVariants: {

      variant:

        "primary",

      size:

        "md",

    },

  },

);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({

  className,

  variant,

  size,

  children,

  ...props

}: BadgeProps) {

  return (

    <span

      className={cn(

        badgeVariants({

          variant,

          size,

        }),

        className,

      )}

      {...props}

    >

      {children}

    </span>

  );

}

export { badgeVariants };