"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import {
  BarChart3,
  LayoutDashboard,
  LogOut,
  Settings,
  TrendingUp,
  History,
  Activity
} from "lucide-react"

import { cn } from "@/lib/utils"
import { authApi } from "@/lib/api/auth"

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Stocks & Predictions", href: "/stocks", icon: TrendingUp },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "History", href: "/history", icon: History },
  { name: "Backtesting", href: "/backtesting", icon: Activity },
  { name: "Settings", href: "/settings", icon: Settings },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const router = useRouter()

  const handleLogout = async () => {
    try {
      await authApi.logout()
    } catch (e) {
      // ignore
    } finally {
      localStorage.removeItem("auth_token")
      router.push("/login")
    }
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-card flex-shrink-0 flex flex-col transition-all duration-300">
        <div className="h-16 flex items-center px-6 border-b border-border/50">
          <Link href="/dashboard" className="flex items-center gap-2 text-primary">
            <TrendingUp className="w-6 h-6" />
            <span className="text-lg font-bold tracking-tight text-foreground">TradePredict</span>
          </Link>
        </div>

        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-200 group relative",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                )}
              >
                {isActive && (
                  <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-primary rounded-r-full" />
                )}
                <item.icon
                  className={cn(
                    "w-5 h-5",
                    isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                  )}
                />
                {item.name}
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-border/50">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium text-muted-foreground hover:bg-destructive/10 hover:text-destructive w-full transition-colors"
          >
            <LogOut className="w-5 h-5" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Subtle background glow */}
        <div className="absolute top-[-10%] right-[-5%] w-[40%] h-[40%] bg-primary/5 rounded-full blur-[100px] pointer-events-none" />
        
        <div className="flex-1 overflow-y-auto p-6 md:p-8 relative z-10">
          <div className="max-w-7xl mx-auto h-full">
            {children}
          </div>
        </div>
      </main>
    </div>
  )
}
