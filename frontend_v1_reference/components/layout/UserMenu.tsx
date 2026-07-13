"use client";

import { ChevronDown } from "lucide-react";

export function UserMenu() {
  return (
    <button
      className="flex items-center gap-2 rounded-[8px] border border-[#E8EDF2] bg-white px-2.5 py-1.5 text-[13px] transition-all duration-150 hover:bg-[#F7F9FC] hover:border-[#D7DEE7]"
      aria-label="User menu"
    >
      <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[#0066FF] text-[10px] font-bold text-white shrink-0">
        U
      </div>
      <div className="hidden text-left xl:block">
        <p className="text-[13px] font-semibold text-[#11131A] leading-tight">User</p>
      </div>
      <ChevronDown size={12} className="text-[#8B95A5] shrink-0" />
    </button>
  );
}