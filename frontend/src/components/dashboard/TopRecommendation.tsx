import {
  ArrowUpRight,
  Target,
  TrendingUp,
  Trophy,
  ShieldAlert,
} from "lucide-react";

import type { ContractRecommendation } from "../../services/api";
import EmptyState from "./EmptyState";
import ScoreCard from "./ScoreCard";

interface TopRecommendationProps {
  recommendation: ContractRecommendation | null;
}

function TopRecommendation({
  recommendation,
}: TopRecommendationProps) {
  if (!recommendation) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-slate-500">
              Top Recommendation
            </p>

            <h2 className="mt-1 text-xl font-bold text-slate-900">
              Decision Result
            </h2>
          </div>

          <div className="rounded-xl bg-amber-50 p-3 text-amber-600">
            <Trophy size={22} />
          </div>
        </div>

        <EmptyState message="No recommendation available yet." />
      </div>
    );
  }

  const finalScore = recommendation.final_score;

  const normalizedScore =
    finalScore === null
      ? 0
      : Math.min(Math.max(finalScore, 0), 100);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-500">
            Top Recommendation
          </p>

          <h2 className="mt-1 text-xl font-bold text-slate-900">
            Decision Result
          </h2>
        </div>

        <div className="rounded-xl bg-amber-50 p-3 text-amber-600">
          <Trophy size={22} />
        </div>
      </div>

      <div className="rounded-xl bg-slate-50 p-4">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
          Contract
        </p>

        <p className="mt-1 truncate text-base font-bold text-slate-900">
          {recommendation.contract_name ?? "Unnamed Contract"}
        </p>

        <p className="mt-1 text-xs text-slate-500">
          {recommendation.contract_id}
        </p>
      </div>

      <div className="mt-5 flex items-end justify-between">
        <div>
          <p className="text-xs font-medium text-slate-500">
            Final Score
          </p>

          <p className="mt-1 text-4xl font-bold text-indigo-600">
            {finalScore === null
              ? "N/A"
              : finalScore.toFixed(2)}
          </p>
        </div>

        <div className="rounded-lg bg-indigo-50 px-3 py-2 text-sm font-semibold text-indigo-700">
          Rank #{recommendation.rank ?? "—"}
        </div>
      </div>

      <div className="mt-5">
        <div className="mb-2 flex justify-between text-xs">
          <span className="text-slate-500">
            Decision score
          </span>

          <span className="font-semibold text-slate-700">
            {finalScore === null
              ? "N/A"
              : `${finalScore.toFixed(1)}%`}
          </span>
        </div>

        <div className="h-2 overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-indigo-600 transition-all"
            style={{
              width: `${normalizedScore}%`,
            }}
          />
        </div>
      </div>

      <div className="mt-6 grid gap-4">
        <ScoreCard
          title="Financial"
          score={recommendation.financial_score}
          icon={<TrendingUp size={18} />}
        />

        <ScoreCard
          title="Risk"
          score={recommendation.risk_score}
          icon={<ShieldAlert size={18} />}
        />

        <ScoreCard
          title="Contract Value"
          score={recommendation.contract_value_score}
          icon={<Target size={18} />}
        />
      </div>

      <div className="mt-6 rounded-xl border border-slate-100 bg-slate-50 p-4">
        <div className="flex items-start gap-3">
          <ArrowUpRight
            size={19}
            className="mt-0.5 text-indigo-600"
          />

          <div>
            <p className="text-sm font-semibold text-slate-900">
              Analysis Explanation
            </p>

            <p className="mt-1 text-sm leading-6 text-slate-600">
              {recommendation.explanation ??
                "No explanation is available."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TopRecommendation;