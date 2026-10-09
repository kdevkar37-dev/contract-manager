import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  AlertTriangle,
  ArrowLeft,
  Bot,
  CheckCircle2,
  Clock3,
  FileText,
  HelpCircle,
  Loader2,
  MessageSquare,
  ShieldAlert,
  TrendingUp,
  XCircle,
} from "lucide-react";

import {
  askContract,
  getContract,
  getContractDocumentStatus,
  getContractRisks,
  getFinancialAnalysis,
  getFinalDecision,
  getFinalDecisionHistory,
  getRecommendations,
  createFinalDecision,
  type Contract,
  type ContractAskResponse,
  type ContractDocumentStatus,
  type FinancialAnalysis,
  type FinalDecision,
  type ContractRecommendation,
  type RiskAnalysis,
} from "../services/api";

function formatValue(value: string | null): string {
  if (value === null || value === undefined || value === "") {
    return "Insufficient data";
  }

  return value;
}

function formatConfidence(confidence: string | null): string {
  if (!confidence) {
    return "Not available";
  }

  const numericConfidence = Number(confidence);

  if (!Number.isNaN(numericConfidence)) {
    return `${(numericConfidence * 100).toFixed(0)}%`;
  }

  return confidence;
}

function getSeverityClass(severity: string): string {
  switch (severity.toLowerCase()) {
    case "critical":
      return "border-red-200 bg-red-50 text-red-700";

    case "high":
      return "border-orange-200 bg-orange-50 text-orange-700";

    case "medium":
      return "border-yellow-200 bg-yellow-50 text-yellow-700";

    case "low":
      return "border-emerald-200 bg-emerald-50 text-emerald-700";

    default:
      return "border-slate-200 bg-slate-50 text-slate-700";
  }
}

function getStatusConfig(status: string) {
  const normalizedStatus = status.toLowerCase();

  if (normalizedStatus === "completed") {
    return {
      label: "Completed",
      className: "border-emerald-200 bg-emerald-50 text-emerald-700",
      icon: <CheckCircle2 size={16} />,
    };
  }

  if (normalizedStatus === "failed") {
    return {
      label: "Failed",
      className: "border-red-200 bg-red-50 text-red-700",
      icon: <XCircle size={16} />,
    };
  }

  if (normalizedStatus === "processing" || normalizedStatus === "pending") {
    return {
      label: "Processing",
      className: "border-amber-200 bg-amber-50 text-amber-700",
      icon: <Clock3 size={16} />,
    };
  }

  return {
    label: status,
    className: "border-slate-200 bg-slate-50 text-slate-700",
    icon: <FileText size={16} />,
  };
}

function FinancialMetric({
  label,
  value,
}: {
  label: string;
  value: string | null;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <p className="text-sm text-slate-500">{label}</p>

      <p className="mt-2 text-lg font-semibold text-slate-900">
        {formatValue(value)}
      </p>
    </div>
  );
}

export default function ContractDetails() {
  const { contractId: routeContractId } = useParams<{
    contractId: string;
  }>();

  const [contract, setContract] = useState<Contract | null>(null);

  const [documentStatus, setDocumentStatus] =
    useState<ContractDocumentStatus | null>(null);

  const [financialAnalysis, setFinancialAnalysis] =
    useState<FinancialAnalysis | null>(null);

  const [risks, setRisks] = useState<RiskAnalysis[]>([]);

  const [recommendation, setRecommendation] =
    useState<ContractRecommendation | null>(null);

  const [finalDecision, setFinalDecision] = useState<FinalDecision | null>(
    null,
  );

  const [decisionHistory, setDecisionHistory] = useState<FinalDecision[]>([]);

  const [decision, setDecision] = useState("Review");

  const [decisionReason, setDecisionReason] = useState("");

  const [savingDecision, setSavingDecision] = useState(false);

  const [question, setQuestion] = useState("");

  const [answer, setAnswer] = useState<ContractAskResponse | null>(null);

  const [loading, setLoading] = useState(true);

  const [asking, setAsking] = useState(false);

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!routeContractId) {
      setError("Contract ID is missing.");
      setLoading(false);
      return;
    }

    const contractId = routeContractId;

    let intervalId: ReturnType<typeof setInterval> | null = null;

    async function loadAnalysisData() {
      try {
        const financialData = await getFinancialAnalysis(contractId);

        setFinancialAnalysis(financialData);
      } catch {
        setFinancialAnalysis(null);
      }

      try {
        const riskData = await getContractRisks(contractId);

        setRisks(riskData);
      } catch {
        setRisks([]);
      }

      try {
        const recommendationData = await getRecommendations();

        const currentRecommendation =
          recommendationData.recommendations.find(
            (item) => item.contract_id === contractId,
          ) ?? null;

        setRecommendation(currentRecommendation);
      } catch {
        setRecommendation(null);
      }

      try {
        const currentDecision = await getFinalDecision(contractId);

        setFinalDecision(currentDecision);

        const historyData = await getFinalDecisionHistory(contractId);

        setDecisionHistory(historyData);
      } catch {
        setFinalDecision(null);
        setDecisionHistory([]);
      }
    }

    async function loadContract() {
      try {
        setError(null);

        const contractData = await getContract(contractId);

        setContract(contractData);
        setLoading(false);

        let documentData: ContractDocumentStatus | null = null;

        try {
          documentData = await getContractDocumentStatus(contractId);

          setDocumentStatus(documentData);
        } catch (documentError) {
          console.warn(
            "Document status is not available for this contract:",
            documentError,
          );

          setDocumentStatus(null);
        }

        await loadAnalysisData();

        const contractStatus = contractData.status.toLowerCase();

        const documentProcessingStatus =
          documentData?.processing_status?.toLowerCase();

        if (
          contractStatus === "processing" ||
          contractStatus === "pending" ||
          documentProcessingStatus === "processing" ||
          documentProcessingStatus === "pending"
        ) {
          intervalId = setInterval(async () => {
            try {
              const updatedContract = await getContract(contractId);

              setContract(updatedContract);

              try {
                const updatedDocument =
                  await getContractDocumentStatus(contractId);

                setDocumentStatus(updatedDocument);

                if (
                  updatedContract.status.toLowerCase() === "completed" ||
                  updatedContract.status.toLowerCase() === "failed" ||
                  updatedDocument.processing_status.toLowerCase() ===
                    "completed" ||
                  updatedDocument.processing_status.toLowerCase() === "failed"
                ) {
                  await loadAnalysisData();

                  if (intervalId) {
                    clearInterval(intervalId);
                    intervalId = null;
                  }
                }
              } catch (documentError) {
                console.warn(
                  "Document status refresh unavailable:",
                  documentError,
                );
              }
            } catch (refreshError) {
              console.error("Failed to refresh contract status:", refreshError);
            }
          }, 3000);
        }
      } catch (loadError) {
        console.error("Failed to load contract:", loadError);

        setError("Failed to load contract details.");
        setLoading(false);
      }
    }
    void loadContract();

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [routeContractId]);

  async function handleAskQuestion() {
    if (!routeContractId || !question.trim()) {
      return;
    }

    try {
      setAsking(true);
      setAnswer(null);
      setError(null);

      const result = await askContract(routeContractId, question.trim());

      setAnswer(result);
    } catch (askError) {
      console.error("Failed to ask contract question:", askError);

      setError("Failed to get an answer from the contract.");
    } finally {
      setAsking(false);
    }
  }

  async function handleFinalDecision() {
    if (!routeContractId || !decision.trim() || !decisionReason.trim()) {
      setError("Decision and reason are required.");
      return;
    }

    try {
      setSavingDecision(true);
      setError(null);

      const savedDecision = await createFinalDecision(
        routeContractId,
        decision.trim(),
        decisionReason.trim(),
      );

      setFinalDecision(savedDecision);

      setDecisionHistory((currentHistory) => [
        savedDecision,
        ...currentHistory.filter((item) => item.id !== savedDecision.id),
      ]);

      setDecisionReason("");
    } catch (decisionError) {
      console.error("Failed to save final decision:", decisionError);

      setError(
        decisionError instanceof Error
          ? decisionError.message
          : "Failed to save the final decision.",
      );
    } finally {
      setSavingDecision(false);
    }
  }

  if (loading) {
    return (
      <div className="mx-auto flex min-h-[400px] max-w-7xl items-center justify-center">
        <div className="flex items-center gap-3 text-sm text-slate-500">
          <Loader2 size={20} className="animate-spin" />
          Loading contract...
        </div>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="mx-auto max-w-7xl">
        <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
          <p className="font-medium text-red-700">Contract not found.</p>

          <Link
            to="/contracts"
            className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-red-700 hover:underline"
          >
            <ArrowLeft size={16} />
            Back to Contracts
          </Link>
        </div>
      </div>
    );
  }

  const status = getStatusConfig(contract.status);

  return (
    <div className="mx-auto max-w-7xl">
      {/* Back */}

      <Link
        to="/contracts"
        className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-slate-600 transition hover:text-slate-900"
      >
        <ArrowLeft size={17} />
        Back to Contracts
      </Link>

      {/* Header */}

      <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex items-start gap-4">
            <div className="rounded-xl bg-indigo-50 p-3 text-indigo-600">
              <FileText size={26} />
            </div>

            <div>
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-2xl font-bold text-slate-900">
                  {contract.name}
                </h1>

                <span
                  className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${status.className}`}
                >
                  {status.icon}

                  {status.label}
                </span>
              </div>

              <p className="mt-2 text-sm text-slate-500">
                Contract ID: {contract.contract_id}
              </p>

              {contract.description && (
                <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
                  {contract.description}
                </p>
              )}
            </div>
          </div>

          <div className="rounded-xl bg-slate-50 px-4 py-3">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Source
            </p>

            <p className="mt-1 text-sm font-semibold text-slate-700">
              {contract.source_type}
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 border-t border-slate-100 pt-6 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <p className="text-xs text-slate-400">Contract ID</p>

            <p className="mt-1 text-sm font-medium text-slate-700">
              {contract.contract_id}
            </p>
          </div>

          <div>
            <p className="text-xs text-slate-400">File</p>

            <p className="mt-1 truncate text-sm font-medium text-slate-700">
              {contract.original_filename || "Not available"}
            </p>
          </div>

          <div>
            <p className="text-xs text-slate-400">Start Date</p>

            <p className="mt-1 text-sm font-medium text-slate-700">
              {contract.start_date || "Not available"}
            </p>
          </div>

          <div>
            <p className="text-xs text-slate-400">End Date</p>

            <p className="mt-1 text-sm font-medium text-slate-700">
              {contract.end_date || "Not available"}
            </p>
          </div>
        </div>
      </div>

      {/* Error */}

      {error && (
        <div className="mb-6 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <ShieldAlert size={19} className="mt-0.5 shrink-0" />

          <span>{error}</span>
        </div>
      )}

      {/* Processing */}

      <section className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-5 flex items-center gap-3">
          <div className="rounded-lg bg-slate-100 p-2.5 text-slate-700">
            <Clock3 size={21} />
          </div>

          <div>
            <h2 className="font-semibold text-slate-900">
              Document Processing
            </h2>

            <p className="text-sm text-slate-500">
              Current document processing state.
            </p>
          </div>
        </div>

        {documentStatus ? (
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Processing Status</p>

              <p className="mt-2 font-semibold capitalize text-slate-900">
                {documentStatus.processing_status}
              </p>
            </div>

            <div className="rounded-xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Processed At</p>

              <p className="mt-2 font-semibold text-slate-900">
                {documentStatus.processed_at || "Not available"}
              </p>
            </div>

            {documentStatus.error_message && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-4 sm:col-span-2">
                <p className="text-sm font-semibold text-red-700">
                  Processing Error
                </p>

                <p className="mt-1 text-sm text-red-600">
                  {documentStatus.error_message}
                </p>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-slate-500">
            Document processing information is not available yet.
          </p>
        )}
      </section>

      {/* Financial Analysis */}

      <section className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex items-center gap-3">
          <div className="rounded-lg bg-emerald-50 p-2.5 text-emerald-600">
            <TrendingUp size={21} />
          </div>

          <div>
            <h2 className="font-semibold text-slate-900">Financial Analysis</h2>

            <p className="text-sm text-slate-500">
              Financial metrics extracted and calculated from the contract.
            </p>
          </div>
        </div>

        {!financialAnalysis ? (
          <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
            <p className="text-sm text-slate-500">
              Financial analysis is not available yet.
            </p>
          </div>
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <FinancialMetric
                label="Revenue"
                value={financialAnalysis.revenue}
              />

              <FinancialMetric
                label="Initial Investment"
                value={financialAnalysis.initial_investment}
              />

              <FinancialMetric
                label="Fixed Costs"
                value={financialAnalysis.fixed_costs}
              />

              <FinancialMetric
                label="Variable Costs"
                value={financialAnalysis.variable_costs}
              />

              <FinancialMetric
                label="Total Cost"
                value={financialAnalysis.total_cost}
              />

              <FinancialMetric
                label="Profit"
                value={financialAnalysis.profit}
              />

              <FinancialMetric
                label="ROI"
                value={
                  financialAnalysis.roi ? `${financialAnalysis.roi}%` : null
                }
              />

              <FinancialMetric
                label="Profit Margin"
                value={
                  financialAnalysis.profit_margin
                    ? `${financialAnalysis.profit_margin}%`
                    : null
                }
              />

              <FinancialMetric
                label="Break Even"
                value={financialAnalysis.break_even}
              />
            </div>

            {financialAnalysis.assumptions.length > 0 && (
              <div className="mt-6 rounded-xl border border-slate-200 p-5">
                <div className="mb-3 flex items-center gap-2">
                  <HelpCircle size={18} className="text-slate-500" />

                  <h3 className="font-semibold text-slate-900">Assumptions</h3>
                </div>

                <ul className="space-y-2">
                  {financialAnalysis.assumptions.map((assumption, index) => (
                    <li
                      key={index}
                      className="flex gap-2 text-sm text-slate-600"
                    >
                      <span>•</span>

                      <span>{assumption}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {financialAnalysis.sources.length > 0 && (
              <div className="mt-6 rounded-xl border border-slate-200 p-5">
                <h3 className="mb-3 font-semibold text-slate-900">Sources</h3>

                <ul className="space-y-2">
                  {financialAnalysis.sources.map((source, index) => (
                    <li key={index} className="text-sm text-slate-600">
                      • {source}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </section>

      {/* Risk Analysis */}

      <section className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-orange-50 p-2.5 text-orange-600">
              <AlertTriangle size={21} />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">Risk Analysis</h2>

              <p className="text-sm text-slate-500">
                Identified contractual risks and evidence.
              </p>
            </div>
          </div>

          <span className="rounded-full bg-slate-100 px-3 py-1.5 text-sm font-semibold text-slate-700">
            {risks.length} {risks.length === 1 ? "Risk" : "Risks"}
          </span>
        </div>

        {risks.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
            <CheckCircle2 size={30} className="mx-auto mb-3 text-emerald-500" />

            <p className="text-sm font-medium text-slate-700">
              No meaningful risks were identified for this contract.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {risks.map((risk) => (
              <div
                key={risk.id}
                className="rounded-xl border border-slate-200 p-5"
              >
                <div className="mb-3 flex flex-wrap items-center gap-2">
                  <span
                    className={`rounded-full border px-3 py-1 text-xs font-semibold ${getSeverityClass(
                      risk.severity,
                    )}`}
                  >
                    {risk.severity.toUpperCase()}
                  </span>

                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                    {risk.risk_type}
                  </span>
                </div>

                <h3 className="text-lg font-semibold text-slate-900">
                  {risk.title}
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {risk.description}
                </p>

                {risk.evidence && (
                  <div className="mt-4 rounded-lg bg-slate-50 p-4">
                    <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Evidence
                    </p>

                    <p className="text-sm leading-6 text-slate-700">
                      {risk.evidence}
                    </p>
                  </div>
                )}

                <div className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                  {risk.source && (
                    <div>
                      <span className="font-semibold text-slate-700">
                        Source:
                      </span>{" "}
                      <span className="text-slate-600">{risk.source}</span>
                    </div>
                  )}

                  <div>
                    <span className="font-semibold text-slate-700">
                      Confidence:
                    </span>{" "}
                    <span className="text-slate-600">
                      {formatConfidence(risk.confidence)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Decision Analysis */}

      <section className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex items-center gap-3">
          <div className="rounded-lg bg-violet-50 p-2.5 text-violet-600">
            <TrendingUp size={21} />
          </div>

          <div>
            <h2 className="font-semibold text-slate-900">Decision Analysis</h2>

            <p className="text-sm text-slate-500">
              Transparent deterministic scoring used to support the
              manager&apos;s review.
            </p>
          </div>
        </div>

        {!recommendation ? (
          <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
            <p className="text-sm text-slate-500">
              Decision analysis is not available for this contract yet.
            </p>
          </div>
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {[
                ["Final Score", recommendation.final_score],
                ["Financial Score", recommendation.financial_score],
                ["Risk Score", recommendation.risk_score],
                ["Contract Value Score", recommendation.contract_value_score],
              ].map(([label, value]) => (
                <div
                  key={String(label)}
                  className="rounded-xl border border-slate-200 bg-slate-50 p-4"
                >
                  <p className="text-sm text-slate-500">{label}</p>

                  <p className="mt-2 text-2xl font-bold text-slate-900">
                    {value ?? "Insufficient data"}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-5">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Explanation
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-700">
                {recommendation.explanation || "No explanation is available."}
              </p>
            </div>

            <div className="mt-6 rounded-xl border border-indigo-100 bg-indigo-50/50 p-5">
              <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900">
                    Manager Final Decision
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    Record the manager&apos;s final decision and supporting
                    reason.
                  </p>
                </div>

                {finalDecision && (
                  <span className="w-fit rounded-full bg-white px-3 py-1.5 text-xs font-semibold text-slate-700">
                    Current: {finalDecision.decision}
                  </span>
                )}
              </div>

              <div className="grid gap-4 lg:grid-cols-[220px_1fr]">
                <div>
                  <label
                    htmlFor="final-decision"
                    className="mb-2 block text-sm font-medium text-slate-700"
                  >
                    Decision
                  </label>

                  <select
                    id="final-decision"
                    value={decision}
                    onChange={(event) => setDecision(event.target.value)}
                    disabled={savingDecision}
                    className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 disabled:bg-slate-50"
                  >
                    <option value="Approve">Approve</option>

                    <option value="Reject">Reject</option>

                    <option value="Review">Review</option>
                  </select>
                </div>

                <div>
                  <label
                    htmlFor="decision-reason"
                    className="mb-2 block text-sm font-medium text-slate-700"
                  >
                    Reason
                  </label>

                  <textarea
                    id="decision-reason"
                    value={decisionReason}
                    onChange={(event) => setDecisionReason(event.target.value)}
                    placeholder="Enter the reason supporting this decision..."
                    rows={3}
                    disabled={savingDecision}
                    className="w-full resize-none rounded-xl border border-slate-300 bg-white p-4 text-sm text-slate-900 outline-none placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 disabled:bg-slate-50"
                  />
                </div>
              </div>

              <button
                type="button"
                onClick={() => void handleFinalDecision()}
                disabled={savingDecision || !decisionReason.trim()}
                className="mt-4 inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {savingDecision ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    Saving Decision...
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={18} />
                    Save Final Decision
                  </>
                )}
              </button>
            </div>

            {decisionHistory.length > 0 && (
              <div className="mt-6 rounded-xl border border-slate-200 p-5">
                <h3 className="font-semibold text-slate-900">
                  Decision History
                </h3>

                <div className="mt-4 space-y-3">
                  {decisionHistory.map((item) => (
                    <div
                      key={item.id}
                      className="rounded-xl border border-slate-200 bg-slate-50 p-4"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <span className="font-semibold text-slate-900">
                          {item.decision}
                        </span>

                        <span className="text-xs text-slate-500">
                          {new Date(item.created_at).toLocaleString()}
                        </span>
                      </div>

                      <p className="mt-2 text-sm leading-6 text-slate-600">
                        {item.reason}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </section>

      {/* Contract Q&A */}

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex items-center gap-3">
          <div className="rounded-lg bg-indigo-50 p-2.5 text-indigo-600">
            <Bot size={21} />
          </div>

          <div>
            <h2 className="font-semibold text-slate-900">
              Ask About This Contract
            </h2>

            <p className="text-sm text-slate-500">
              Ask questions and receive answers grounded in the contract
              documents.
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Example: What is the contract value?"
            rows={4}
            className="w-full resize-none rounded-xl border border-slate-300 p-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
          />

          <button
            type="button"
            onClick={() => void handleAskQuestion()}
            disabled={asking || !question.trim()}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {asking ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <MessageSquare size={18} />
                Ask Question
              </>
            )}
          </button>
        </div>

        {answer && (
          <div className="mt-6 rounded-xl border border-indigo-100 bg-indigo-50/50 p-5">
            <div className="flex items-center gap-2">
              <Bot size={19} className="text-indigo-600" />

              <h3 className="font-semibold text-slate-900">Answer</h3>
            </div>

            <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700">
              {answer.answer}
            </p>

            {answer.sources.length > 0 && (
              <div className="mt-6">
                <h3 className="mb-3 text-sm font-semibold text-slate-900">
                  Evidence Sources
                </h3>

                <div className="space-y-3">
                  {answer.sources.map((source, index) => (
                    <div
                      key={index}
                      className="rounded-xl border border-slate-200 bg-white p-4"
                    >
                      <div className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                        <FileText size={15} />

                        <span>Document {source.document_id}</span>

                        <span className="text-slate-400">•</span>

                        <span>Chunk {source.chunk_index}</span>
                      </div>

                      <p className="mt-2 text-sm leading-6 text-slate-600">
                        {source.evidence}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}
