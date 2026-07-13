export function DashboardLoading() {
  return (
    <div className="animate-fade-in">
      <div className="grid grid-cols-12 gap-4 lg:gap-5">
        {/* Prediction card skeleton */}
        <div className="col-span-12 xl:col-span-6">
          <div className="rounded-[16px] border border-[#E8EDF2] bg-white p-5 h-[240px]">
            <div className="skeleton h-2.5 w-20 rounded mb-5" />
            <div className="skeleton h-8 w-24 rounded mb-2" />
            <div className="skeleton h-4 w-14 rounded mb-5" />
            <div className="skeleton h-2.5 w-full rounded mb-2" />
            <div className="skeleton h-1.5 w-full rounded-full" />
          </div>
        </div>
        {/* Price card skeleton */}
        <div className="col-span-12 xl:col-span-6">
          <div className="rounded-[16px] border border-[#E8EDF2] bg-white p-5 h-[240px]">
            <div className="skeleton h-2.5 w-20 rounded mb-5" />
            <div className="skeleton h-7 w-28 rounded mb-1.5" />
            <div className="skeleton h-2.5 w-16 rounded mb-5" />
            <div className="grid grid-cols-2 gap-3 pt-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i}>
                  <div className="skeleton h-2 w-8 rounded mb-1.5" />
                  <div className="skeleton h-3.5 w-16 rounded" />
                </div>
              ))}
            </div>
          </div>
        </div>
        {/* Bottom cards */}
        {[1, 2].map((i) => (
          <div key={i} className="col-span-12 lg:col-span-6">
            <div className="rounded-[16px] border border-[#E8EDF2] bg-white p-5 h-[200px]">
              <div className="skeleton h-2.5 w-20 rounded mb-5" />
              <div className="skeleton h-6 w-24 rounded mb-3" />
              <div className="grid grid-cols-2 gap-3 rounded-[10px] bg-[#F7F9FC] p-3.5">
                {[1, 2, 3, 4].map((j) => (
                  <div key={j}>
                    <div className="skeleton h-2 w-10 rounded mb-1.5" />
                    <div className="skeleton h-3 w-14 rounded" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}