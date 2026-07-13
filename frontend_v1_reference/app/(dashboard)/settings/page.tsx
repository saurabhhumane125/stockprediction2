"use client";

import { useSettings } from "@/features/settings";

import { SettingsLoading } from "@/features/settings/components/SettingsLoading";

import { SettingsError } from "@/features/settings/components/SettingsError";

import { SettingsGrid } from "@/features/settings/components/SettingsGrid";

import { ProfileCard } from "@/features/settings/components/ProfileCard";

import { AppInfoCard } from "@/features/settings/components/AppInfoCard";

import { ApiStatusCard } from "@/features/settings/components/ApiStatusCard";

export default function SettingsPage() {

  const {

    data,

    loading,

    error,

  } = useSettings();

  if (loading) {

    return <SettingsLoading />;

  }

  if (error || !data) {

    return (

      <SettingsError

        message={

          error ??

          "Unable to load settings."

        }

      />

    );

  }

  return (

    <SettingsGrid>

      <div className="col-span-12 lg:col-span-6">

        <ProfileCard

          user={data.user}

        />

      </div>

      <div className="col-span-12 lg:col-span-6">

        <AppInfoCard

          appName={data.appName}

          version={data.version}

        />

      </div>

      <div className="col-span-12">

        <ApiStatusCard

          status={data.apiStatus}

        />

      </div>

    </SettingsGrid>

  );

}