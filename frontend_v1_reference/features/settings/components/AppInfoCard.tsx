import {
  Card,
  CardContent,
  CardLabel,
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
    <Card className="p-6">
      <CardContent className="space-y-5">
        <CardLabel>Application</CardLabel>

        <div className="space-y-4">
          <div className="flex items-center justify-between py-2 border-b border-[#F0F4F8]">
            <span className="text-[15px] font-medium text-[#5B6473]">Name</span>
            <span className="text-[15px] font-bold text-[#11131A]">{appName}</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-[15px] font-medium text-[#5B6473]">Version</span>
            <span className="text-[15px] font-bold text-[#11131A] font-tabular">{version}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}