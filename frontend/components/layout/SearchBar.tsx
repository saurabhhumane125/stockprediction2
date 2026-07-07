"use client";

import { Search } from "lucide-react";

export function SearchBar() {

  return (

    <div className="relative w-[360px] max-w-full">

      <Search
        size={18}
        className="
          absolute
          left-5
          top-1/2
          -translate-y-1/2
          text-[#5B6473]
        "
      />

      <input

        placeholder="Search stocks..."

        className="
          h-14
          w-full
          rounded-2xl
          border
          border-[#D7DEE7]
          bg-white
          pl-14
          pr-5
          text-[#11131A]
          shadow-sm
          transition-all
          duration-300
          placeholder:text-[#8892A0]
          focus:border-[#0066FF]
          focus:ring-4
          focus:ring-blue-100
          focus:outline-none
        "

      />

    </div>

  );

}