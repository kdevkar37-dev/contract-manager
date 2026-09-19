import type { ReactNode } from "react";

interface ScoreCardProps {
  title: string;
  score: number | null;
  icon: ReactNode;
}

function ScoreCard({
  title,
  score,
  icon,
}: ScoreCardProps) {
  const normalizedScore =
    score === null
      ? 0
      : Math.min(Math.max(score, 0), 100);

  return (
    <div className="rounded-xl border border-slate-200 p-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
          {icon}

          {title}
        </div>

        <span className="text-xl font-bold text-slate-900">
          {score === null ? "—" : score.toFixed(2)}
        </span>
      </div>

      <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full rounded-full bg-indigo-500 transition-all"
          style={{
            width: `${normalizedScore}%`,
          }}
        />
      </div>
    </div>
  );
}

export default ScoreCard;