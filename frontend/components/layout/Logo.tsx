import { TrendingUp } from "lucide-react";

export function Logo() {

  return (

    <div
      className="
        flex
        h-14
        w-14
        items-center
        justify-center
        rounded-[20px]
        bg-gradient-to-br
        from-[#0066FF]
        to-[#4F8CFF]
        shadow-lg
      "
    >

      <TrendingUp
        className="text-white"
        size={28}
      />

    </div>

  );

}