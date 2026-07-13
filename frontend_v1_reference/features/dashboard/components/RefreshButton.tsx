"use client";

import { RotateCw } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface RefreshButtonProps {
  loading: boolean;
  onRefresh: () => void;
}

export function RefreshButton({
  loading,
  onRefresh,
}: RefreshButtonProps) {
  return (
    <Button
      variant="outline"
      size="sm"
      onClick={onRefresh}
      disabled={loading}
    >
      <RotateCw
        size={14}
        className={loading ? "animate-spin" : ""}
      />
      Refresh
    </Button>
  );
}