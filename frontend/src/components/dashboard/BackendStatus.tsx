import { Activity } from "lucide-react";

interface BackendStatusProps {
  status: string;
}

function BackendStatus({ status }: BackendStatusProps) {
  const isChecking = status === "Checking...";
  const isUnavailable = status === "Backend unavailable";

  return (
    <div className="mb-6 flex items-center justify-between rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
      <div className="flex items-center gap-3">
        <Activity size={20} className="text-slate-500" />

        <div>
          <p className="text-sm font-medium text-slate-900">
            Backend System
          </p>

          <p className="text-xs text-slate-500">
            API connectivity status
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <span
          className={`h-2.5 w-2.5 rounded-full ${
            isChecking
              ? "bg-amber-500"
              : isUnavailable
                ? "bg-red-500"
                : "bg-emerald-500"
          }`}
        />

        <span className="text-sm font-semibold text-slate-700">
          {status}
        </span>
      </div>
    </div>
  );
}

export default BackendStatus;