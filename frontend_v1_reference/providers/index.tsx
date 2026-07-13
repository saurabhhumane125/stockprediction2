"use client";

import { ToastProvider } from "./ToastProvider";

export default function Providers({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <ToastProvider />
      {children}
    </>
  );
}