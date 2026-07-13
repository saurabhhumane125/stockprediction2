"use client";

import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

export function DashboardShell({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex h-screen overflow-hidden bg-[#EDF1F5]">
      {/* Fixed-width sidebar */}
      <Sidebar />

      {/* Main content area */}
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-[1400px] px-5 py-6 lg:px-6 lg:py-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}