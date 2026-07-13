import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/cn";

const badgeVariants = cva(
  [
    "inline-flex",
    "items-center",
    "justify-center",
    "gap-1.5",
    "rounded-full",
    "font-bold",
    "tracking-wide",
    "transition-colors duration-150",
    "select-none",
    "whitespace-nowrap",
  ].join(" "),
  {
    variants: {
      variant: {
        primary:
          "bg-[#0066FF] text-white px-3 py-1 text-[13px]",

        accent:
          "bg-[#B4FF00] text-[#11131A] px-3 py-1 text-[13px]",

        secondary:
          "bg-[#F0F4F8] text-[#5B6473] px-3 py-1 text-[13px]",

        success:
          "bg-[#ECFFD6] text-[#3D6600] px-3 py-1 text-[13px]",

        warning:
          "bg-[#FFF6E0] text-[#7A5200] px-3 py-1 text-[13px]",

        danger:
          "bg-[#FFE5E5] text-[#CC0000] px-3 py-1 text-[13px]",

        outline:
          "border border-[#E8EDF2] bg-white text-[#5B6473] px-3 py-1 text-[13px]",

        neutral:
          "bg-[#F0F4F8] text-[#5B6473] px-3 py-1 text-[13px]",

        buy:
          "bg-[#B4FF00] text-[#1A3300] px-3 py-1 text-[13px] tracking-wider",

        sell:
          "bg-[#FFE5E5] text-[#CC0000] px-3 py-1 text-[13px] tracking-wider",

        hold:
          "bg-[#F0F4F8] text-[#5B6473] px-3 py-1 text-[13px] tracking-wider",
      },

      size: {
        sm: "px-2.5 py-0.5 text-xs",
        md: "",
        lg: "px-4 py-1.5 text-sm",
      },
    },

    defaultVariants: {
      variant: "primary",
      size: "md",
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
      className={cn(badgeVariants({ variant, size }), className)}
      {...props}
    >
      {children}
    </span>
  );
}

export { badgeVariants };