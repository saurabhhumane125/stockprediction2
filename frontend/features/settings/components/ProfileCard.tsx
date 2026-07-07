import {

  Card,

  CardContent,

  CardHeader,

  CardTitle,

} from "@/components/ui/Card";

import type {

  SettingsUser,

} from "../types/settings.types";

interface ProfileCardProps {

  user: SettingsUser;

}

export function ProfileCard({

  user,

}: Readonly<ProfileCardProps>) {

  return (

    <Card>

      <CardHeader>

        <CardTitle>

          Profile

        </CardTitle>

      </CardHeader>

      <CardContent className="space-y-4">

        <div>

          <p className="text-sm text-slate-500">

            Name

          </p>

          <p className="font-medium">

            {user.full_name}

          </p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Email

          </p>

          <p className="font-medium">

            {user.email}

          </p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Status

          </p>

          <p className="font-medium">

            {user.is_active

              ? "Active"

              : "Inactive"}

          </p>

        </div>

      </CardContent>

    </Card>

  );

}