import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/cn";

const cardVariants = cva(
  [
    "rounded-[16px]",
    "border",
    "border-[#E8EDF2]",
    "bg-white",
    "transition-all",
    "duration-150",
  ].join(" "),
  {
    variants: {
      variant: {
        default:
          "shadow-[0_1px_3px_rgba(17,19,26,0.04)]",

        elevated:
          "shadow-[0_2px_8px_rgba(17,19,26,0.06)]",

        outline:
          "bg-transparent shadow-none",

        ghost:
          "border-transparent bg-transparent shadow-none",

        accent:
          [
            "border-[#1A1F2E]",
            "bg-[#11131A]",
            "text-white",
            "shadow-[0_2px_8px_rgba(17,19,26,0.15)]",
          ].join(" "),
      },

      padding: {
        none: "p-0",
        sm: "p-5",
        md: "p-6",
        lg: "p-8",
      },

      hoverable: {
        true: [
          "hover:shadow-[0_4px_16px_rgba(17,19,26,0.08)]",
          "hover:-translate-y-[1px]",
          "cursor-pointer",
        ].join(" "),
        false: "",
      },
    },

    defaultVariants: {
      variant: "default",
      padding: "md",
      hoverable: false,
    },
  }
);

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

export function Card({
  className,
  variant,
  padding,
  hoverable,
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        cardVariants({ variant, padding, hoverable }),
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "mb-6 flex items-start justify-between gap-5",
        className,
      )}
      {...props}
    />
  );
}

export function CardTitle({
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={cn(
        "text-lg font-bold tracking-tight text-[#11131A] font-[family-name:var(--font-space-grotesk)]",
        className,
      )}
      {...props}
    />
  );
}

export function CardDescription({
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn(
        "mt-1.5 text-[15px] leading-relaxed text-[#5B6473]",
        className,
      )}
      {...props}
    />
  );
}

export function CardContent({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(className)}
      {...props}
    />
  );
}

export function CardFooter({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "mt-6 flex items-center justify-end gap-4",
        className,
      )}
      {...props}
    />
  );
}

export function CardLabel({
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn(
        "text-[13px] font-semibold uppercase tracking-[0.1em] text-[#8B95A5]",
        className,
      )}
      {...props}
    />
  );
}