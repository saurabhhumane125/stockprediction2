"use client";

import { usePathname } from "next/navigation";

import { Breadcrumb } from "./Breadcrumb";
import { NotificationBell } from "./NotificationBell";
import { SearchBar } from "./SearchBar";
import { UserMenu } from "./UserMenu";

const TITLES: Record<string, string> = {

  "/dashboard": "Dashboard",

  "/prediction": "Prediction",

  "/analytics": "Analytics",

  "/history": "History",

  "/backtesting": "Backtesting",

  "/stocks": "Stocks",

  "/settings": "Settings",

};

export function Header() {

  const pathname = usePathname();

  const title = TITLES[pathname] ?? "Dashboard";

  return (

    <header

      className="
        sticky
        top-0
        z-40
        border-b
        border-[#D7DEE7]
        bg-[#EDF1F5]/90
        backdrop-blur-xl
      "

    >

      <div

        className="
          flex
          h-24
          items-center
          justify-between
          px-8
          lg:px-10
        "

      >

        <div className="space-y-2">

          <Breadcrumb

            items={[

              {

                label: "Home",

                href: "/dashboard",

              },

              {

                label: title,

              },

            ]}

          />

          <h1

            className="
              text-4xl
              font-bold
              tracking-tight
              text-[#11131A]
            "

          >

            {title}

          </h1>

        </div>

        <div

          className="
            flex
            items-center
            gap-4
          "

        >

          <SearchBar />

          <NotificationBell />

          <UserMenu />

        </div>

      </div>

    </header>

  );

}