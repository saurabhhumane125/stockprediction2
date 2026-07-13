"use client";

import { useEffect } from "react";

import { ContentGrid } from "@/components/layout/ContentGrid";

import { useHistory } from "@/features/history";

import { HistoryLoading } from "@/features/history/components/HistoryLoading";
import { HistoryError } from "@/features/history/components/HistoryError";
import { HistoryEmpty } from "@/features/history/components/HistoryEmpty";
import { HistoryTable } from "@/features/history/components/HistoryTable";

export default function HistoryPage() {

  const {

    data,

    loading,

    error,

    refresh,

  } = useHistory();

  useEffect(() => {

    refresh();

  }, [refresh]);

  if (loading) {

    return <HistoryLoading />;

  }

  if (error) {

    return (

      <HistoryError

        message={error}

      />

    );

  }

  if (

    !data ||

    data.history.length === 0

  ) {

    return <HistoryEmpty />;

  }

  return (

    <ContentGrid>

      <div className="col-span-12">

        <HistoryTable

          history={data.history}

        />

      </div>

    </ContentGrid>

  );

}