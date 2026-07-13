import type { ReactNode } from "react";
import { Card } from "@/components/ui/Card";

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: ReactNode;
  description?: string;
}

export function StatCard({
  title,
  value,
  icon,
  description,
}: StatCardProps) {
  return (
    <Card className="h-full">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wider text-[#8B95A5]">
            {title}
          </p>
          <h2 className="mt-3 text-3xl font-bold text-[#11131A] font-tabular font-[family-name:var(--font-space-grotesk)]">
            {value}
          </h2>
          {description && (
            <p className="mt-2 text-sm text-[#5B6473]">
              {description}
            </p>
          )}
        </div>
        {icon && (
          <div className="rounded-[10px] bg-[#F0F4F8] p-2.5">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}