import type { ReactNode } from "react";

interface DashboardStatCardProps {
  title: string;
  value: number | string;
  description: string;
  icon: ReactNode;
}

function DashboardStatCard({
  title,
  value,
  description,
  icon,
}: DashboardStatCardProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">
            {title}
          </p>

          <p className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
            {value}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            {description}
          </p>
        </div>

        <div className="rounded-xl bg-indigo-50 p-3 text-indigo-600">
          {icon}
        </div>
      </div>
    </div>
  );
}

export default DashboardStatCard;