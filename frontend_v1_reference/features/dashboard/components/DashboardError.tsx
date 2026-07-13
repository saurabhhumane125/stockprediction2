import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface Props {
  message: string;
  onRetry?: () => void;
}

export function DashboardError({ message, onRetry }: Props) {
  return (
    <div className="flex flex-col items-center justify-center rounded-[16px] border border-[#FFE5E5] bg-[#FFFBFB] py-16 text-center">
      <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-[10px] bg-[#FFE5E5]">
        <AlertCircle size={20} className="text-[#FF3B3B]" />
      </div>
      <h3 className="text-[14px] font-semibold text-[#11131A] mb-1">
        Unable to load dashboard
      </h3>
      <p className="max-w-sm text-[13px] leading-5 text-[#5B6473] mb-5">
        {message || "An unexpected error occurred. Please try again."}
      </p>
      {onRetry && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
        >
          <RefreshCw size={13} />
          Try again
        </Button>
      )}
    </div>
  );
}