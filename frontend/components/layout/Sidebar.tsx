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

  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },

  {
    title: "Prediction",
    href: "/prediction",
    icon: TrendingUp,
  },

  {
    title: "Analytics",
    href: "/analytics",
    icon: BarChart3,
  },

  {
    title: "History",
    href: "/history",
    icon: History,
  },

  {
    title: "Backtesting",
    href: "/backtesting",
    icon: BrainCircuit,
  },

  {
    title: "Stocks",
    href: "/stocks",
    icon: CandlestickChart,
  },

  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
  },

];

export function Sidebar() {

  const pathname = usePathname();

  const router = useRouter();

  async function handleLogout() {

    try {

      await logout();

    }

    finally {

      router.replace("/login");

      router.refresh();

    }

  }

  return (

    <aside
      className="
      sticky
      top-0
      flex
      h-screen
      w-[290px]
      shrink-0
      flex-col
      border-r
      border-[#D7DEE7]
      bg-white
      shadow-sm
    "
    >

      <div className="px-7 py-8">

        <Brand />

      </div>

      <nav className="flex-1 space-y-2 px-5">

        {navigation.map((item) => {

          const Icon = item.icon;

          const active = pathname === item.href;

          return (

            <Link
              key={item.href}
              href={item.href}
              className={cn(

                "group flex items-center gap-4 rounded-2xl px-5 py-4 transition-all duration-300",

                active
                  ? "bg-[#0066FF] text-white shadow-lg shadow-blue-500/20"
                  : "text-[#5B6473] hover:bg-[#EDF1F5] hover:text-[#11131A]"

              )}
            >

              <Icon
                size={20}
                strokeWidth={2.2}
              />

              <span className="font-semibold">

                {item.title}

              </span>

            </Link>

          );

        })}

      </nav>

      <div className="border-t border-[#D7DEE7] p-5">

        <button

          onClick={handleLogout}

          className="
            flex
            w-full
            items-center
            justify-center
            gap-3
            rounded-2xl
            border
            border-[#FFD4D4]
            bg-white
            py-3
            font-semibold
            text-[#FF3B3B]
            transition-all
            duration-300
            hover:bg-[#FFF2F2]
          "

        >

          <LogOut size={18} />

          Logout

        </button>

      </div>

    </aside>

  );

}