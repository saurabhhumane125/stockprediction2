interface SettingsGridProps {

  children: React.ReactNode;

}

export function SettingsGrid({

  children,

}: Readonly<SettingsGridProps>) {

  return (

    <div className="grid grid-cols-12 gap-6">

      {children}

    </div>

  );

}