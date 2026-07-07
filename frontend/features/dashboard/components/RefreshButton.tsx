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
      variant="secondary"
      onClick={onRefresh}
      disabled={loading}
    >

      <RotateCw
        size={18}
        className={loading ? "animate-spin" : ""}
      />

      <span className="ml-2">

        Refresh

      </span>

    </Button>

  );

}