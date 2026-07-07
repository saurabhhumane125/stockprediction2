import { APP } from "@/lib/app";

import { Logo } from "./Logo";

export function Brand() {

  return (

    <div className="flex items-center gap-4">

      <Logo />

      <div>

        <h2
          className="
            font-['Space_Grotesk']
            text-xl
            font-bold
            text-[#11131A]
          "
        >

          {APP.name}

        </h2>

        <p
          className="
            mt-1
            text-sm
            text-[#5B6473]
          "
        >

          {APP.tagline}

        </p>

      </div>

    </div>

  );

}