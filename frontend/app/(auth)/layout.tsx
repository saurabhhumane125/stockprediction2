import { AuthHero } from "@/features/auth/components/AuthHero";
import { AuthLayout } from "@/features/auth/components/AuthLayout";

export default function Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {

  return (

    <AuthLayout
      hero={<AuthHero />}
    >

      {children}

    </AuthLayout>

  );

}