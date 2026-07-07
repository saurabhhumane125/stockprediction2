import {

  Card,

  CardContent,

  CardHeader,

  CardTitle,

} from "@/components/ui/Card";

interface AppInfoCardProps {

  appName: string;

  version: string;

}

export function AppInfoCard({

  appName,

  version,

}: Readonly<AppInfoCardProps>) {

  return (

    <Card>

      <CardHeader>

        <CardTitle>

          Application

        </CardTitle>

      </CardHeader>

      <CardContent className="space-y-4">

        <div>

          <p className="text-sm text-slate-500">

            Name

          </p>

          <p>

            {appName}

          </p>

        </div>

        <div>

          <p className="text-sm text-slate-500">

            Version

          </p>

          <p>

            {version}

          </p>

        </div>

      </CardContent>

    </Card>

  );

}