import type { ReactNode } from "react";

interface Props {

  hero: ReactNode;

  children: ReactNode;

}

export function AuthLayout({

  hero,

  children,

}: Props) {

  return (

    <main
      className="
        relative
        min-h-screen
        overflow-hidden
        bg-[#EDF1F5]
      "
    >

      <div
        className="
          absolute
          left-[-220px]
          top-[-180px]
          h-[520px]
          w-[520px]
          rounded-full
          bg-[#0066FF]/10
          blur-[140px]
        "
      />

      <div
        className="
          absolute
          bottom-[-220px]
          right-[-120px]
          h-[460px]
          w-[460px]
          rounded-full
          bg-[#B4FF00]/20
          blur-[150px]
        "
      />

      <div
        className="
          relative
          mx-auto
          flex
          min-h-screen
          max-w-[1700px]
          items-center
          px-12
          py-10
        "
      >

        <div
          className="
            grid
            w-full
            grid-cols-12
            items-center
            gap-14
          "
        >

          <section className="col-span-7">

            {hero}

          </section>

          <section
            className="
              col-span-5
              flex
              justify-center
            "
          >

            {children}

          </section>

        </div>

      </div>

    </main>

  );

}