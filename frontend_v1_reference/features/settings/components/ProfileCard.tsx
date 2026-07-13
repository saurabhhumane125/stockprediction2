import { Card, CardContent, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { SettingsUser } from "../types/settings.types";

interface ProfileCardProps {
  user: SettingsUser;
}

const Field = ({ label, value }: { label: string; value: string }) => (
  <div>
    <p className="text-[13px] font-semibold uppercase tracking-[0.08em] text-[#8B95A5] mb-2">
      {label}
    </p>
    <p className="text-[15px] font-medium text-[#11131A]">{value}</p>
  </div>
);

export function ProfileCard({ user }: Readonly<ProfileCardProps>) {
  return (
    <Card padding="none">
      <div className="flex items-center justify-between px-6 py-5 border-b border-[#F0F4F8]">
        <CardTitle>Profile</CardTitle>
        <Badge variant={user.is_active ? "success" : "danger"} size="lg">
          {user.is_active ? "Active" : "Inactive"}
        </Badge>
      </div>

      <CardContent className="p-6 space-y-6">
        {/* Avatar row */}
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[#0066FF] text-white text-[20px] font-bold shrink-0">
            {user.full_name?.charAt(0)?.toUpperCase() ?? "U"}
          </div>
          <div>
            <p className="text-[18px] font-bold text-[#11131A] tracking-tight">{user.full_name}</p>
            <p className="text-[15px] text-[#5B6473]">{user.email}</p>
          </div>
        </div>

        {/* Fields */}
        <div className="grid grid-cols-1 gap-5 border-t border-[#F0F4F8] pt-5 sm:grid-cols-2">
          <Field label="Full Name" value={user.full_name} />
          <Field label="Email" value={user.email} />
          <Field label="Account Status" value={user.is_active ? "Active" : "Inactive"} />
        </div>
      </CardContent>
    </Card>
  );
}