import type { ReactNode } from "react";

interface Props {
  children: ReactNode;
}

export function AuthCard({
  children,
}: Props) {
  return (
    <div className="w-full">
      {children}
    </div>
  );
}