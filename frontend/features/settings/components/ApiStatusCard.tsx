import {

  Card,

  CardContent,

  CardHeader,

  CardTitle,

} from "@/components/ui/Card";

import { Badge } from "@/components/ui/Badge";

interface ApiStatusCardProps {

  status: string;

}

export function ApiStatusCard({

  status,

}: Readonly<ApiStatusCardProps>) {

  return (

    <Card>

      <CardHeader>

        <CardTitle>

          API Status

        </CardTitle>

      </CardHeader>

      <CardContent>

        <Badge

          variant="success"

        >

          {status}

        </Badge>

      </CardContent>

    </Card>

  );

}