import type { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  breadcrumbs?: {
    label: string;
    href?: string;
  }[];
}

export function PageHeader({
  title,
  subtitle,
  actions,
  breadcrumbs,
}: PageHeaderProps) {
  return (
    <section className="mb-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl lg:text-4xl font-bold tracking-tight text-[#11131A] font-[family-name:var(--font-space-grotesk)]">
            {title}
          </h1>
          {subtitle && (
            <p className="mt-2 max-w-2xl text-[15px] lg:text-base leading-relaxed text-[#5B6473]">
              {subtitle}
            </p>
          )}
        </div>

        {actions && (
          <div className="shrink-0">
            {actions}
          </div>
        )}
      </div>
    </section>
  );
}