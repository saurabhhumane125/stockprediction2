"use client";

import { Bell } from "lucide-react";

export function NotificationBell() {
  return (
    <button
      className="
        relative
        flex
        h-9
        w-9
        items-center
        justify-center
        rounded-[8px]
        border
        border-[#E8EDF2]
        bg-white
        transition-all
        duration-150
        hover:bg-[#F7F9FC]
        hover:border-[#D7DEE7]
      "
    >
      <Bell
        size={16}
        strokeWidth={1.8}
        className="text-[#5B6473]"
      />
      <span
        className="
          absolute
          right-2
          top-2
          h-[7px]
          w-[7px]
          rounded-full
          bg-[#FF3B3B]
          ring-[1.5px]
          ring-white
        "
      />
    </button>
  );
}