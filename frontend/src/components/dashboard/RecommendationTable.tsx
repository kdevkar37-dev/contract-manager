import { ArrowUpRight } from "lucide-react";

import type { ContractRecommendation } from "../../services/api";
import EmptyState from "./EmptyState";

interface RecommendationTableProps {
  recommendations: ContractRecommendation[];
}

function formatScore(score: number | null) {
  return score === null ? "—" : score.toFixed(2);
}

function RecommendationTable({ recommendations }: RecommendationTableProps) {
  return (
    <div className="mt-8 rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex flex-col gap-3 border-b border-slate-100 p-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-500">
            Contract Analysis
          </p>

          <h2 className="mt-1 text-xl font-bold text-slate-900">
            Recommendations
          </h2>
        </div>

        <span className="w-fit rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-600">
          {recommendations.length} analyzed
        </span>
      </div>

      {recommendations.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[800px] text-left">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-6 py-4">Rank</th>

                <th className="px-6 py-4">Contract</th>

                <th className="px-6 py-4">Financial</th>

                <th className="px-6 py-4">Risk</th>

                <th className="px-6 py-4">Value</th>

                <th className="px-6 py-4">Final Score</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-100">
              {recommendations.map((recommendation) => (
                <tr
                  key={recommendation.contract_id}
                  className="transition hover:bg-slate-50"
                >
                  <td className="px-6 py-4">
                    <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 text-sm font-bold text-slate-700">
                      {recommendation.rank ?? "—"}
                    </span>
                  </td>

                  <td className="px-6 py-4">
                    <p className="font-semibold text-slate-900">
                      {recommendation.contract_name ?? "Unnamed Contract"}
                    </p>

                    <p className="mt-1 text-xs text-slate-400">
                      {recommendation.contract_id}
                    </p>
                  </td>

                  <td className="px-6 py-4 text-sm font-medium text-slate-700">
                    {formatScore(recommendation.financial_score)}
                  </td>

                  <td className="px-6 py-4 text-sm font-medium text-slate-700">
                    {formatScore(recommendation.risk_score)}
                  </td>

                  <td className="px-6 py-4 text-sm font-medium text-slate-700">
                    {formatScore(recommendation.contract_value_score)}
                  </td>

                  <td className="px-6 py-4">
                    <span className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-50 px-3 py-1.5 text-sm font-bold text-indigo-700">
                      {recommendation.final_score === null
                        ? "N/A"
                        : recommendation.final_score.toFixed(2)}

                      <ArrowUpRight size={14} />
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="p-10">
          <EmptyState message="No eligible contract recommendations available." />
        </div>
      )}
    </div>
  );
}

export default RecommendationTable;
