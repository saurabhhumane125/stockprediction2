import { APP } from "@/lib/app";
import { Logo } from "./Logo";

export function Brand() {
  return (
    <div className="flex items-center gap-2.5 min-w-0">
      <Logo />
      <div className="min-w-0">
        <h2 className="text-[13px] font-bold leading-tight text-[#11131A] truncate font-[family-name:var(--font-space-grotesk)]">
          {APP.shortName}
        </h2>
        <p className="text-[10px] text-[#8B95A5] font-medium truncate leading-tight">
          Prediction Platform
        </p>
      </div>
    </div>
  );
}