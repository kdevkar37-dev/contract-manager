import { useEffect, useState } from "react";
import {
  BarChart3,
  CheckCircle2,
  FileText,
  RefreshCw,
  ShieldAlert,
} from "lucide-react";

import {
  getContracts,
  getRecommendations,
  healthCheck,
  runDecisionWorkflow,
  type Contract,
  type ContractRecommendation,
} from "../services/api";

import BackendStatus from "../components/dashboard/BackendStatus";
import DashboardStatCard from "../components/dashboard/DashboardStatCard";
import RecommendationTable from "../components/dashboard/RecommendationTable";
import TopRecommendation from "../components/dashboard/TopRecommendation";

function Dashboard() {
  const [status, setStatus] = useState("Checking...");

  const [contracts, setContracts] = useState<Contract[]>([]);

  const [recommendations, setRecommendations] = useState<
    ContractRecommendation[]
  >([]);

  const [loading, setLoading] = useState(true);

  const [workflowLoading, setWorkflowLoading] = useState(false);

  const [error, setError] = useState("");

  useEffect(() => {
    void loadDashboard();
  }, []);

  async function loadDashboard() {
    setLoading(true);
    setError("");

    const results = await Promise.allSettled([
      healthCheck(),
      getContracts(),
      getRecommendations(),
    ]);

    let hasError = false;

    // ---------------------------------------------------------
    // Health
    // ---------------------------------------------------------

    if (results[0].status === "fulfilled") {
      const health = results[0].value;

      setStatus(health?.status ? String(health.status) : "Connected");
    } else {
      setStatus("Backend unavailable");
      hasError = true;

      console.error("Health check failed:", results[0].reason);
    }

    // ---------------------------------------------------------
    // Contracts
    // ---------------------------------------------------------

    if (results[1].status === "fulfilled") {
      setContracts(results[1].value);
    } else {
      setContracts([]);
      hasError = true;

      console.error("Failed to load contracts:", results[1].reason);
    }

    // ---------------------------------------------------------
    // Recommendations
    // ---------------------------------------------------------

    if (results[2].status === "fulfilled") {
      setRecommendations(results[2].value.recommendations);
    } else {
      setRecommendations([]);
      hasError = true;

      console.error("Failed to load recommendations:", results[2].reason);
    }

    if (hasError) {
      setError(
        "Some dashboard data could not be loaded. Please check the backend API.",
      );
    }

    setLoading(false);
  }

  async function handleRunWorkflow() {
    try {
      setWorkflowLoading(true);
      setError("");

      const result = await runDecisionWorkflow();

      setRecommendations(result.recommendations);

      await loadDashboard();
    } catch (workflowError) {
      console.error("Decision workflow failed:", workflowError);

      setError("Decision workflow failed. Please try again.");
    } finally {
      setWorkflowLoading(false);
    }
  }

  const completedContracts = contracts.filter(
    (contract) => contract.status.toLowerCase() === "completed",
  ).length;

  const processingContracts = contracts.filter((contract) => {
    const contractStatus = contract.status.toLowerCase();

    return contractStatus === "processing" || contractStatus === "pending";
  }).length;

  const failedContracts = contracts.filter(
    (contract) => contract.status.toLowerCase() === "failed",
  ).length;

  const topRecommendation =
    recommendations.length > 0 ? recommendations[0] : null;

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      {/* -------------------------------------------------------
          Header
      ------------------------------------------------------- */}

      <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-indigo-600 p-3 text-white shadow-sm">
              <BarChart3 size={24} />
            </div>

            <div>
              <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                Contract Dashboard
              </h1>

              <p className="mt-1 text-sm text-slate-500">
                Monitor contracts, risks, financial performance and decisions.
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={handleRunWorkflow}
          disabled={workflowLoading}
          className="flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <RefreshCw
            size={18}
            className={workflowLoading ? "animate-spin" : ""}
          />

          {workflowLoading ? "Analyzing Contracts..." : "Run Decision Analysis"}
        </button>
      </div>

      {/* -------------------------------------------------------
          Error
      ------------------------------------------------------- */}

      {error && (
        <div className="mb-6 flex items-center gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <ShieldAlert size={18} />

          <span>{error}</span>
        </div>
      )}

      {/* -------------------------------------------------------
          Backend Status
      ------------------------------------------------------- */}

      <BackendStatus status={status} />

      {/* -------------------------------------------------------
          Statistics
      ------------------------------------------------------- */}

      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <DashboardStatCard
          title="Total Contracts"
          value={loading ? "—" : contracts.length}
          description="Contracts in system"
          icon={<FileText size={22} />}
        />

        <DashboardStatCard
          title="Completed"
          value={loading ? "—" : completedContracts}
          description="Successfully processed"
          icon={<CheckCircle2 size={22} />}
        />

        <DashboardStatCard
          title="Processing"
          value={loading ? "—" : processingContracts}
          description="Pending analysis"
          icon={<RefreshCw size={22} />}
        />

        <DashboardStatCard
          title="Failed"
          value={loading ? "—" : failedContracts}
          description="Requires attention"
          icon={<ShieldAlert size={22} />}
        />
      </div>

      {/* -------------------------------------------------------
          Decision Section
      ------------------------------------------------------- */}

      <div className="mt-8">
        <TopRecommendation recommendation={topRecommendation} />
      </div>

      {/* -------------------------------------------------------
          Recommendations
      ------------------------------------------------------- */}

      <RecommendationTable recommendations={recommendations} />
    </div>
  );
}

export default Dashboard;
