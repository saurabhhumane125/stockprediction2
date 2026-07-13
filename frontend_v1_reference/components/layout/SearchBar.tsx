"use client";

import { Search } from "lucide-react";

export function SearchBar() {
  return (
    <div className="relative w-[220px] max-w-full hidden md:block">
      <Search
        size={15}
        className="
          absolute
          left-3
          top-1/2
          -translate-y-1/2
          text-[#8B95A5]
        "
      />
      <input
        placeholder="Search stocks..."
        className="
          h-9
          w-full
          rounded-[8px]
          border
          border-[#E8EDF2]
          bg-[#F7F9FC]
          pl-9
          pr-3
          text-[13px]
          text-[#11131A]
          transition-all
          duration-150
          placeholder:text-[#9BA5B4]
          focus:bg-white
          focus:border-[#0066FF]
          focus:ring-[3px]
          focus:ring-[#0066FF]/8
          focus:outline-none
        "
      />
      <div className="absolute right-2.5 top-1/2 -translate-y-1/2 hidden lg:flex items-center gap-0.5 text-[10px] text-[#B0BAC5] font-medium">
        <kbd className="px-1 py-0.5 rounded bg-white border border-[#E8EDF2] shadow-[0_1px_1px_rgba(0,0,0,0.04)] font-mono text-[10px]">⌘</kbd>
        <kbd className="px-1 py-0.5 rounded bg-white border border-[#E8EDF2] shadow-[0_1px_1px_rgba(0,0,0,0.04)] font-mono text-[10px]">K</kbd>
      </div>
    </div>
  );
}