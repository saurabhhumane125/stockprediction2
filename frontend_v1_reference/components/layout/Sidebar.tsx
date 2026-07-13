"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  TrendingUp,
  BarChart3,
  History,
  BrainCircuit,
  CandlestickChart,
  Settings,
  LogOut,
} from "lucide-react";
import { Brand } from "./Brand";
import { cn } from "@/lib/cn";
import { logout } from "@/features/auth/api/auth.api";

const navigation = [
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { title: "Prediction", href: "/prediction", icon: TrendingUp },
  { title: "Analytics", href: "/analytics", icon: BarChart3 },
  { title: "History", href: "/history", icon: History },
  { title: "Backtesting", href: "/backtesting", icon: BrainCircuit },
  { title: "Stocks", href: "/stocks", icon: CandlestickChart },
  { title: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  async function handleLogout() {
    try {
      await logout();
    } finally {
      router.replace("/login");
      router.refresh();
    }
  }

  return (
    <aside className="flex h-screen w-[260px] shrink-0 flex-col border-r border-[#E8EDF2] bg-white">
      {/* Brand */}
      <div className="flex h-16 shrink-0 items-center border-b border-[#E8EDF2] px-6">
        <Brand />
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
        {navigation.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group relative flex items-center gap-3 rounded-[10px] px-3 py-2.5 text-[15px] font-medium transition-all duration-150",
                active
                  ? "bg-[#0066FF]/[0.06] text-[#0066FF]"
                  : "text-[#5B6473] hover:bg-[#F0F4F8] hover:text-[#11131A]"
              )}
            >
              {/* Active indicator bar */}
              {active && (
                <span className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-full bg-[#0066FF]" />
              )}

              <Icon
                size={20}
                strokeWidth={active ? 2.2 : 1.8}
                className={cn(
                  "shrink-0 transition-colors duration-150",
                  active ? "text-[#0066FF]" : "text-[#8B95A5] group-hover:text-[#5B6473]"
                )}
              />
              <span>{item.title}</span>
            </Link>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="shrink-0 border-t border-[#E8EDF2] p-4">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-[10px] px-3 py-2.5 text-[15px] font-medium text-[#5B6473] transition-all duration-150 hover:bg-[#FFF0F0] hover:text-[#FF3B3B]"
        >
          <LogOut size={20} strokeWidth={1.8} className="shrink-0" />
          Logout
        </button>
      </div>
    </aside>
  );
}