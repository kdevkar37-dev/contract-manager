import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

import {
  askContract,
  getContract,
  getContractDocumentStatus,
  getContractRisks,
  getFinancialAnalysis,
  type Contract,
  type ContractDocumentStatus,
  type ContractAskResponse,
  type FinancialAnalysis,
  type RiskAnalysis,
} from "../services/api";


function formatValue(value: string | null): string {
  if (value === null || value === undefined || value === "") {
    return "Insufficient data";
  }

  return value;
}


function getSeverityClass(severity: string): string {
  switch (severity.toLowerCase()) {
    case "critical":
      return "bg-red-100 text-red-800 border-red-300";

    case "high":
      return "bg-orange-100 text-orange-800 border-orange-300";

    case "medium":
      return "bg-yellow-100 text-yellow-800 border-yellow-300";

    case "low":
      return "bg-green-100 text-green-800 border-green-300";

    default:
      return "bg-gray-100 text-gray-800 border-gray-300";
  }
}


function formatConfidence(
  confidence: string | null
): string {
  if (!confidence) {
    return "Not available";
  }

  const numericConfidence = Number(confidence);

  if (!Number.isNaN(numericConfidence)) {
    return `${(numericConfidence * 100).toFixed(0)}%`;
  }

  return confidence;
}


export default function ContractDetails() {
  const { contractId } = useParams<{
    contractId: string;
  }>();

  const [contract, setContract] =
    useState<Contract | null>(null);

  const [documentStatus, setDocumentStatus] =
    useState<ContractDocumentStatus | null>(null);

  const [financialAnalysis, setFinancialAnalysis] =
    useState<FinancialAnalysis | null>(null);

  const [risks, setRisks] =
    useState<RiskAnalysis[]>([]);

  const [question, setQuestion] =
    useState("");

  const [answer, setAnswer] =
    useState<ContractAskResponse | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [asking, setAsking] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    if (!contractId) {
      return;
    }

    let intervalId: ReturnType<typeof setInterval> | null =
      null;

    const loadContract = async () => {
      try {
        setError(null);

        const contractData =
          await getContract(contractId);

        setContract(contractData);

        const documentData =
          await getContractDocumentStatus(contractId);

        setDocumentStatus(documentData);

        try {
          const financialData =
            await getFinancialAnalysis(contractId);

          setFinancialAnalysis(financialData);
        } catch {
          setFinancialAnalysis(null);
        }

        try {
          const riskData =
            await getContractRisks(contractId);

          setRisks(riskData);
        } catch {
          setRisks([]);
        }

        setLoading(false);

        if (
          contractData.status === "processing" ||
          documentData.processing_status === "processing"
        ) {
          intervalId = setInterval(
            async () => {
              try {
                const updatedContract =
                  await getContract(contractId);

                setContract(updatedContract);

                const updatedDocument =
                  await getContractDocumentStatus(
                    contractId
                  );

                setDocumentStatus(updatedDocument);

                if (
                  updatedContract.status === "completed"
                ) {
                  try {
                    const financialData =
                      await getFinancialAnalysis(
                        contractId
                      );

                    setFinancialAnalysis(
                      financialData
                    );
                  } catch {
                    setFinancialAnalysis(null);
                  }

                  try {
                    const riskData =
                      await getContractRisks(
                        contractId
                      );

                    setRisks(riskData);
                  } catch {
                    setRisks([]);
                  }
                }

                if (
                  updatedContract.status === "completed" ||
                  updatedContract.status === "failed"
                ) {
                  if (intervalId) {
                    clearInterval(intervalId);
                    intervalId = null;
                  }
                }
              } catch (err) {
                console.error(
                  "Failed to refresh contract status:",
                  err
                );
              }
            },
            3000
          );
        }
      } catch (err) {
        console.error(
          "Failed to load contract:",
          err
        );

        setError(
          "Failed to load contract details."
        );

        setLoading(false);
      }
    };

    loadContract();

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [contractId]);


  async function handleAskQuestion() {
    if (!contractId || !question.trim()) {
      return;
    }

    try {
      setAsking(true);
      setAnswer(null);
      setError(null);

      const result = await askContract(
        contractId,
        question.trim()
      );

      setAnswer(result);
    } catch (err) {
      console.error(
        "Failed to ask contract question:",
        err
      );

      setError(
        "Failed to get an answer from the contract."
      );
    } finally {
      setAsking(false);
    }
  }


  if (loading) {
    return (
      <div className="p-6">
        <p>Loading contract...</p>
      </div>
    );
  }


  if (!contract) {
    return (
      <div className="p-6">
        <p className="text-red-600">
          Contract not found.
        </p>

        <Link
          to="/contracts"
          className="text-blue-600 hover:underline"
        >
          Back to Contracts
        </Link>
      </div>
    );
  }


  return (
    <div className="p-6 space-y-6">
      <Link
        to="/contracts"
        className="text-blue-600 hover:underline"
      >
        ← Back to Contracts
      </Link>


      {error && (
        <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}


      {/* Contract Information */}

      <section className="rounded-lg border bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-xl font-semibold">
          Contract Information
        </h2>

        <div className="space-y-2">
          <p>
            <strong>Name:</strong>{" "}
            {contract.name}
          </p>

          <p>
            <strong>Contract ID:</strong>{" "}
            {contract.contract_id}
          </p>

          <p>
            <strong>Status:</strong>{" "}
            {contract.status}
          </p>

          <p>
            <strong>Source:</strong>{" "}
            {contract.source_type}
          </p>

          <p>
            <strong>File:</strong>{" "}
            {contract.original_filename ||
              "Not available"}
          </p>

          {contract.description && (
            <p>
              <strong>Description:</strong>{" "}
              {contract.description}
            </p>
          )}

          {contract.start_date && (
            <p>
              <strong>Start Date:</strong>{" "}
              {contract.start_date}
            </p>
          )}

          {contract.end_date && (
            <p>
              <strong>End Date:</strong>{" "}
              {contract.end_date}
            </p>
          )}
        </div>
      </section>


      {/* Document Processing */}

      <section className="rounded-lg border bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-xl font-semibold">
          Document Processing
        </h2>

        {documentStatus ? (
          <div className="space-y-2">
            <p>
              <strong>Processing Status:</strong>{" "}
              {documentStatus.processing_status}
            </p>

            {documentStatus.processed_at && (
              <p>
                <strong>Processed At:</strong>{" "}
                {documentStatus.processed_at}
              </p>
            )}

            {documentStatus.error_message && (
              <p className="text-red-600">
                <strong>Error:</strong>{" "}
                {documentStatus.error_message}
              </p>
            )}
          </div>
        ) : (
          <p>
            Document processing information is not
            available yet.
          </p>
        )}
      </section>


      {/* Financial Analysis */}

      <section className="rounded-lg border bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-xl font-semibold">
          Financial Analysis
        </h2>

        {!financialAnalysis ? (
          <p>
            Financial analysis is not available yet.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Revenue
              </p>

              <p className="text-lg font-semibold">
                {formatValue(
                  financialAnalysis.revenue
                )}
              </p>
            </div>


            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Initial Investment
              </p>

              <p className="text-lg font-semibold">
                {formatValue(
                  financialAnalysis.initial_investment
                )}
              </p>
            </div>


            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Fixed Costs
              </p>

              <p className="text-lg font-semibold">
                {formatValue(
                  financialAnalysis.fixed_costs
                )}
              </p>
            </div>


            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Variable Costs
              </p>

              <p className="text-lg font-semibold">
                {formatValue(
                  financialAnalysis.variable_costs
                )}
              </p>
            </div>


            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Total Cost
              </p>

              <p className="text-lg font-semibold">
                {formatValue(
                  financialAnalysis.total_cost
                )}
              </p>
            </div>


            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Profit
              </p>

              <p className="text-lg font-semibold">
                {formatValue(
                  financialAnalysis.profit
                )}
              </p>
            </div>


            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                ROI
              </p>

              <p className="text-lg font-semibold">
                {formatValue(
                  financialAnalysis.roi
                )}
                {financialAnalysis.roi && "%"}
              </p>
            </div>


            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Profit Margin
              </p>

              <p className="text-lg font-semibold">
                {formatValue(
                  financialAnalysis.profit_margin
                )}
                {financialAnalysis.profit_margin &&
                  "%"}
              </p>
            </div>


            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">
                Break Even
              </p>

              <p className="text-lg font-semibold">
                {formatValue(
                  financialAnalysis.break_even
                )}
              </p>
            </div>
          </div>
        )}


        {financialAnalysis &&
          financialAnalysis.assumptions.length > 0 && (
            <div className="mt-6">
              <h3 className="mb-2 font-semibold">
                Assumptions
              </h3>

              <ul className="list-disc space-y-1 pl-5">
                {financialAnalysis.assumptions.map(
                  (assumption, index) => (
                    <li key={index}>
                      {assumption}
                    </li>
                  )
                )}
              </ul>
            </div>
          )}


        {financialAnalysis &&
          financialAnalysis.sources.length > 0 && (
            <div className="mt-6">
              <h3 className="mb-2 font-semibold">
                Sources
              </h3>

              <ul className="list-disc space-y-1 pl-5">
                {financialAnalysis.sources.map(
                  (source, index) => (
                    <li key={index}>
                      {source}
                    </li>
                  )
                )}
              </ul>
            </div>
          )}
      </section>


      {/* Risk Analysis */}

      <section className="rounded-lg border bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold">
            Risk Analysis
          </h2>

          <span className="rounded-full bg-gray-100 px-3 py-1 text-sm font-medium">
            {risks.length}{" "}
            {risks.length === 1 ? "Risk" : "Risks"}
          </span>
        </div>


        {risks.length === 0 ? (
          <div className="rounded-lg border bg-gray-50 p-4">
            <p className="text-gray-600">
              No meaningful risks were identified for
              this contract.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {risks.map((risk) => (
              <div
                key={risk.id}
                className="rounded-lg border p-5"
              >
                <div className="mb-3 flex flex-wrap items-center gap-2">
                  <span
                    className={`rounded-full border px-3 py-1 text-sm font-semibold ${getSeverityClass(
                      risk.severity
                    )}`}
                  >
                    {risk.severity.toUpperCase()}
                  </span>

                  <span className="rounded-full bg-gray-100 px-3 py-1 text-sm">
                    {risk.risk_type}
                  </span>
                </div>


                <h3 className="mb-2 text-lg font-semibold">
                  {risk.title}
                </h3>


                <p className="mb-4 text-gray-700">
                  {risk.description}
                </p>


                {risk.evidence && (
                  <div className="mb-3 rounded-lg bg-gray-50 p-3">
                    <p className="mb-1 text-sm font-semibold">
                      Evidence
                    </p>

                    <p className="text-sm text-gray-700">
                      {risk.evidence}
                    </p>
                  </div>
                )}


                <div className="grid grid-cols-1 gap-3 text-sm md:grid-cols-2">
                  {risk.source && (
                    <div>
                      <span className="font-semibold">
                        Source:
                      </span>{" "}
                      {risk.source}
                    </div>
                  )}

                  <div>
                    <span className="font-semibold">
                      Confidence:
                    </span>{" "}
                    {formatConfidence(
                      risk.confidence
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>


      {/* Contract Q&A */}

      <section className="rounded-lg border bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-xl font-semibold">
          Ask About This Contract
        </h2>

        <div className="space-y-4">
          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            placeholder="Ask something about this contract..."
            className="min-h-28 w-full rounded-lg border p-3 outline-none focus:ring-2"
          />

          <button
            type="button"
            onClick={handleAskQuestion}
            disabled={
              asking || !question.trim()
            }
            className="rounded-lg px-5 py-2 font-medium disabled:cursor-not-allowed disabled:opacity-50"
          >
            {asking
              ? "Asking..."
              : "Ask Question"}
          </button>
        </div>


        {answer && (
          <div className="mt-6 rounded-lg border bg-gray-50 p-5">
            <h3 className="mb-2 font-semibold">
              Answer
            </h3>

            <p className="whitespace-pre-wrap text-gray-700">
              {answer.answer}
            </p>


            {answer.sources.length > 0 && (
              <div className="mt-5">
                <h3 className="mb-2 font-semibold">
                  Sources
                </h3>

                <div className="space-y-3">
                  {answer.sources.map(
                    (source, index) => (
                      <div
                        key={index}
                        className="rounded-lg border bg-white p-3"
                      >
                        <p className="text-sm font-medium">
                          Document{" "}
                          {source.document_id}
                          {" • "}
                          Chunk{" "}
                          {source.chunk_index}
                        </p>

                        <p className="mt-1 text-sm text-gray-600">
                          {source.evidence}
                        </p>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}