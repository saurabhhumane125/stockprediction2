import { Spinner } from "@/components/ui/Spinner";

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({
  message = "Loading...",
}: Readonly<LoadingStateProps>) {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center gap-4 rounded-2xl border border-slate-200 bg-white">
      <Spinner className="h-8 w-8" />

      <p className="text-sm text-slate-500">
        {message}
      </p>
    </div>
  );
}