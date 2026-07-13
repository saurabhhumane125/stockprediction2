import { Inbox } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description: string;
}

export function EmptyState({
  title,
  description,
}: Readonly<EmptyStateProps>) {
  return (
    <div className="flex flex-col items-center justify-center rounded-[16px] border border-dashed border-[#D7DEE7] bg-white py-14 text-center px-6">
      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-[10px] bg-[#F0F4F8]">
        <Inbox size={18} className="text-[#8B95A5]" />
      </div>
      <h2 className="text-[14px] font-semibold text-[#11131A] mb-1">
        {title}
      </h2>
      <p className="max-w-sm text-[13px] leading-5 text-[#5B6473]">
        {description}
      </p>
    </div>
  );
}