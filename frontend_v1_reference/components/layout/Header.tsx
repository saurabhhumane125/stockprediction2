"use client";

import { usePathname } from "next/navigation";
import { Breadcrumb } from "./Breadcrumb";
import { NotificationBell } from "./NotificationBell";
import { SearchBar } from "./SearchBar";
import { UserMenu } from "./UserMenu";

const PAGE_TITLES: Record<string, { title: string; subtitle: string }> = {
  "/dashboard": {
    title: "Dashboard",
    subtitle: "Real-time market overview and AI prediction summary",
  },
  "/prediction": {
    title: "Prediction",
    subtitle: "Run AI-powered stock trend predictions",
  },
  "/analytics": {
    title: "Analytics",
    subtitle: "Model performance and prediction distribution",
  },
  "/history": {
    title: "History",
    subtitle: "Review all past predictions and results",
  },
  "/backtesting": {
    title: "Backtesting",
    subtitle: "Evaluate historical model performance",
  },
  "/stocks": {
    title: "Stocks",
    subtitle: "Browse and manage supported stocks",
  },
  "/settings": {
    title: "Settings",
    subtitle: "Account, application and system configuration",
  },
};

export function Header() {
  const pathname = usePathname();
  const page = PAGE_TITLES[pathname];

  return (
    <header className="sticky top-0 z-40 flex h-16 shrink-0 items-center border-b border-[#E8EDF2] bg-white/80 backdrop-blur-xl px-6 lg:px-8">
      {/* Left: breadcrumb */}
      <div className="flex flex-1 items-center gap-4 min-w-0">
        {page && (
          <Breadcrumb
            items={[
              { label: "Home", href: "/dashboard" },
              { label: page.title },
            ]}
          />
        )}
      </div>

      {/* Right: controls */}
      <div className="flex shrink-0 items-center gap-3">
        <SearchBar />
        <NotificationBell />
        <UserMenu />
      </div>
    </header>
  );
}