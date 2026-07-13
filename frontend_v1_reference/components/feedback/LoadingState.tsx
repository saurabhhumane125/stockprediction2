import { Spinner } from "@/components/ui/Spinner";

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({
  message = "Loading...",
}: Readonly<LoadingStateProps>) {
  return (
    <div className="flex min-h-[280px] flex-col items-center justify-center gap-3 rounded-[16px] border border-[#E8EDF2] bg-white">
      <Spinner className="h-6 w-6 text-[#0066FF]" />
      <p className="text-[13px] text-[#5B6473]">
        {message}
      </p>
    </div>
  );
}