import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/Card";

import { cn } from "@/lib/cn";

type ChartCardProps = {

  title: string;

  subtitle?: string;

  action?: React.ReactNode;

  children: React.ReactNode;

  className?: string;

};

export function ChartCard({

  title,

  subtitle,

  action,

  children,

  className,

}: ChartCardProps) {

  return (

    <Card
      variant="elevated"
      className={cn(
        "h-full",
        className
      )}
    >

      <CardHeader>

        <div>

          <CardTitle>

            {title}

          </CardTitle>

          {

            subtitle && (

              <CardDescription>

                {subtitle}

              </CardDescription>

            )

          }

        </div>

        {action}

      </CardHeader>

      <CardContent
        className="min-h-[320px]"
      >

        {children}

      </CardContent>

    </Card>

  );

}