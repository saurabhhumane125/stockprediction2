"use client";

import { ChevronDown } from "lucide-react";

export function UserMenu() {

  return (

    <button

      className="
        flex
        items-center
        gap-3
        rounded-2xl
        border
        border-[#D7DEE7]
        bg-white
        px-3
        py-2
        shadow-sm
        transition-all
        duration-300
        hover:-translate-y-0.5
        hover:shadow-lg
      "

    >

      <div

        className="
          flex
          h-11
          w-11
          items-center
          justify-center
          rounded-2xl
          bg-[#0066FF]
          text-sm
          font-bold
          text-white
          shadow-lg
          shadow-blue-500/20
        "

      >

        U

      </div>

      <div

        className="
          hidden
          text-left
          xl:block
        "

      >

        <p

          className="
            text-sm
            font-semibold
            text-[#11131A]
          "

        >

          User

        </p>

        <p

          className="
            text-xs
            text-[#7B8597]
          "

        >

          Signed In

        </p>

      </div>

      <ChevronDown

        size={17}

        className="text-[#5B6473]"

      />

    </button>

  );

}