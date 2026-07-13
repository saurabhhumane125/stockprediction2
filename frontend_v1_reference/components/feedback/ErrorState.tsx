import { AlertCircle } from "lucide-react";

interface ErrorStateProps {
  message: string;
}

export function ErrorState({
  message,
}: Readonly<ErrorStateProps>) {
  return (
    <div className="flex flex-col items-center justify-center rounded-[16px] border border-[#FFE5E5] bg-[#FFFBFB] py-14 text-center px-6">
      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-[10px] bg-[#FFE5E5]">
        <AlertCircle size={18} className="text-[#FF3B3B]" />
      </div>
      <h2 className="text-[14px] font-semibold text-[#11131A] mb-1">
        Something went wrong
      </h2>
      <p className="max-w-sm text-[13px] leading-5 text-[#5B6473]">
        {message}
      </p>
    </div>
  );
}