"use client";

import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

export function DashboardShell({

  children,

}: Readonly<{

  children: React.ReactNode;

}>) {

  return (

    <div className="min-h-screen bg-[#EDF1F5]">

      <div className="flex">

        <Sidebar />

        <div

          className="
            flex
            min-h-screen
            flex-1
            flex-col
            overflow-hidden
          "

        >

          <Header />

          <main

            className="
              flex-1
              overflow-y-auto
              px-6
              py-8
              lg:px-10
            "

          >

            {children}

          </main>

        </div>

      </div>

    </div>

  );

}