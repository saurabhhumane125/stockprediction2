import type { ReactNode } from "react";

interface Props {

  children: ReactNode;

}

export function AuthCard({

  children,

}: Props) {

  return (

    <div
      className="
        w-full
        max-w-[470px]
        rounded-[36px]
        border
        border-white
        bg-white/92
        p-10
        shadow-[0_40px_80px_rgba(17,19,26,0.12)]
        backdrop-blur-xl
      "
    >

      {children}

    </div>

  );

}