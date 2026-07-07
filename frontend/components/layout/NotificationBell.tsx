"use client";

import { Bell } from "lucide-react";

export function NotificationBell() {

  return (

    <button

      className="
        relative
        flex
        h-14
        w-14
        items-center
        justify-center
        rounded-2xl
        border
        border-[#D7DEE7]
        bg-white
        shadow-sm
        transition-all
        duration-300
        hover:-translate-y-0.5
        hover:shadow-lg
      "

    >

      <Bell
        size={21}
        className="text-[#11131A]"
      />

      <span
        className="
          absolute
          right-4
          top-4
          h-3
          w-3
          rounded-full
          bg-[#FF3B3B]
          ring-2
          ring-white
        "
      />

    </button>

  );

}