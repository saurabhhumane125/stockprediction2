import { TrendingUp } from "lucide-react";

export function Logo() {
  return (
    <div
      className="
        flex
        h-8
        w-8
        items-center
        justify-center
        rounded-[8px]
        bg-gradient-to-br
        from-[#0066FF]
        to-[#3385FF]
        shadow-[0_2px_6px_rgba(0,102,255,0.25)]
      "
    >
      <TrendingUp
        className="text-white"
        size={16}
        strokeWidth={2.5}
      />
    </div>
  );
}