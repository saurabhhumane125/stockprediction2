import * as React from "react";

import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/cn";

const cardVariants = cva(

  [
    "rounded-[28px]",
    "border",
    "border-[#D7DEE7]",
    "bg-white",
    "transition-all",
    "duration-300",
    "shadow-sm",
    "hover:-translate-y-1",
    "hover:shadow-xl",
  ].join(" "),

  {

    variants: {

      variant: {

        default:

          "",

        elevated:

          "shadow-xl",

        outline:

          "bg-transparent shadow-none",

        ghost:

          "border-transparent bg-white shadow-none",

        accent:

          [
            "border-transparent",
            "bg-gradient-to-br",
            "from-[#0066FF]",
            "to-[#2B80FF]",
            "text-white",
          ].join(" "),

      },

      padding: {

        none:

          "p-0",

        sm:

          "p-5",

        md:

          "p-7",

        lg:

          "p-9",

      },

    },

    defaultVariants: {

      variant: "default",

      padding: "md",

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

  children,

  ...props

}: CardProps) {

  return (

    <div

      className={cn(

        cardVariants({

          variant,

          padding,

        }),

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

        "mb-7 flex items-start justify-between gap-5",

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

        "text-[22px] font-bold tracking-tight text-[#11131A]",

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

        "mt-2 text-sm leading-6 text-[#5B6473]",

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

        "mt-8 flex items-center justify-end gap-3",

        className,

      )}

      {...props}

    />

  );

}