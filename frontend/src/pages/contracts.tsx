import { useEffect, useState } from "react";

import type { FormEvent } from "react";

import { Link } from "react-router-dom";

import {
  Calendar,
  CheckCircle2,
  ChevronRight,
  Clock3,
  FileText,
  Loader2,
  Plus,
  RefreshCw,
  Upload,
  XCircle,
} from "lucide-react";

import {
  createContract,
  getContractDocumentStatus,
  getContracts,
  uploadContract,
} from "../services/api";

import type { Contract } from "../services/api";

function Contracts() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [contractId, setContractId] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState("");
  const [createSuccess, setCreateSuccess] = useState("");

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");

  const [processingIds, setProcessingIds] = useState<string[]>([]);

  async function loadContracts(showRefresh = false) {
    try {
      if (showRefresh) {
        setRefreshing(true);
      }

      setError("");

      const data = await getContracts();

      setContracts(data);

      const activeProcessingIds = data
        .filter((contract) => {
          const status = contract.status.toLowerCase();

          return status === "processing";
        })
        .map((contract) => contract.contract_id);

      setProcessingIds(activeProcessingIds);
    } catch (loadError) {
      console.error("Failed to load contracts:", loadError);
      setError("Failed to load contracts. Please try again.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    void loadContracts();
  }, []);

  useEffect(() => {
    if (processingIds.length === 0) {
      return;
    }

    const interval = window.setInterval(async () => {
      for (const id of processingIds) {
        try {
          const document = await getContractDocumentStatus(id);

          setContracts((currentContracts) =>
            currentContracts.map((contract) =>
              contract.contract_id === id
                ? {
                    ...contract,
                    status:
                      document.processing_status === "completed"
                        ? "completed"
                        : document.processing_status === "failed"
                          ? "failed"
                          : "processing",
                  }
                : contract,
            ),
          );

          if (
            document.processing_status === "completed" ||
            document.processing_status === "failed"
          ) {
            setProcessingIds((currentIds) =>
              currentIds.filter((currentId) => currentId !== id),
            );
          }
        } catch (pollError) {
          console.error(`Failed to poll contract ${id}:`, pollError);
        }
      }
    }, 2000);

    return () => {
      window.clearInterval(interval);
    };
  }, [processingIds]);

  async function handleCreateContract(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setCreateError("");
    setCreateSuccess("");
    setCreating(true);

    try {
      await createContract({
        contract_id: contractId.trim(),
        name: name.trim(),
        description: description.trim() || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      });

      setCreateSuccess("Contract created successfully.");

      setContractId("");
      setName("");
      setDescription("");
      setStartDate("");
      setEndDate("");

      await loadContracts();
    } catch (createContractError) {
      console.error("Failed to create contract:", createContractError);

      setCreateError("Failed to create contract.");
    } finally {
      setCreating(false);
    }
  }

  async function handleUploadContract(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedFile) {
      setUploadError("Please select a contract file.");
      return;
    }

    setUploadError("");
    setUploadSuccess("");
    setUploading(true);

    try {
      const result = await uploadContract(selectedFile);

      setUploadSuccess(
        `Contract uploaded successfully. ID: ${result.contract_id}`,
      );

      setSelectedFile(null);

      const fileInput = document.getElementById(
        "contractFile",
      ) as HTMLInputElement | null;

      if (fileInput) {
        fileInput.value = "";
      }

      setProcessingIds((currentIds) => [
        ...new Set([...currentIds, result.contract_id]),
      ]);

      await loadContracts();
    } catch (uploadContractError) {
      console.error("Failed to upload contract:", uploadContractError);

      setUploadError(
        "Failed to upload contract. Please check the file and try again.",
      );
    } finally {
      setUploading(false);
    }
  }

  function getStatusConfig(status: string) {
    const normalizedStatus = status.toLowerCase();

    if (normalizedStatus === "completed") {
      return {
        label: "Completed",
        className: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
        icon: <CheckCircle2 size={15} />,
      };
    }

    if (normalizedStatus === "failed") {
      return {
        label: "Failed",
        className: "bg-red-50 text-red-700 ring-red-600/20",
        icon: <XCircle size={15} />,
      };
    }

    if (normalizedStatus === "processing") {
      return {
        label: "Processing",
        className: "bg-amber-50 text-amber-700 ring-amber-600/20",
        icon: <Clock3 size={15} />,
      };
    }

    if (normalizedStatus === "pending") {
      return {
        label: "Pending",
        className: "bg-slate-100 text-slate-700 ring-slate-500/20",
        icon: <Clock3 size={15} />,
      };
    }

    return {
      label: status,
      className: "bg-slate-100 text-slate-700 ring-slate-500/20",
      icon: <FileText size={15} />,
    };
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl">
        <div className="flex min-h-[400px] items-center justify-center">
          <div className="flex items-center gap-3 text-sm text-slate-500">
            <Loader2 size={20} className="animate-spin" />
            Loading contracts...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl">
      {/* Page Header */}
      <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Contracts
          </h1>

          <p className="mt-1 text-sm text-slate-500">
            Upload, create and monitor contracts through the processing
            pipeline.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadContracts(true)}
          disabled={refreshing}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <RefreshCw size={17} className={refreshing ? "animate-spin" : ""} />

          {refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Upload + Manual Creation */}
      <div className="grid gap-6 xl:grid-cols-2">
        {/* Upload */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <div className="rounded-lg bg-indigo-50 p-2.5 text-indigo-600">
              <Upload size={21} />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">Upload Contract</h2>

              <p className="text-sm text-slate-500">
                Upload a PDF, DOCX or TXT contract.
              </p>
            </div>
          </div>

          <form onSubmit={handleUploadContract}>
            <label
              htmlFor="contractFile"
              className="mb-2 block text-sm font-medium text-slate-700"
            >
              Contract File
            </label>

            <label
              htmlFor="contractFile"
              className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center transition hover:border-indigo-400 hover:bg-indigo-50/30"
            >
              <Upload size={30} className="mb-3 text-slate-400" />

              <span className="text-sm font-medium text-slate-700">
                {selectedFile ? selectedFile.name : "Choose a contract file"}
              </span>

              <span className="mt-1 text-xs text-slate-500">
                PDF, DOCX or TXT
              </span>

              <input
                id="contractFile"
                type="file"
                accept=".pdf,.docx,.txt"
                className="hidden"
                onChange={(event) =>
                  setSelectedFile(event.target.files?.[0] ?? null)
                }
              />
            </label>

            {uploadError && (
              <p className="mt-3 text-sm text-red-600">{uploadError}</p>
            )}

            {uploadSuccess && (
              <p className="mt-3 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
                {uploadSuccess}
              </p>
            )}

            <button
              type="submit"
              disabled={uploading}
              className="mt-5 flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {uploading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload size={18} />
                  Upload Contract
                </>
              )}
            </button>
          </form>
        </section>

        {/* Manual Creation */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <div className="rounded-lg bg-slate-100 p-2.5 text-slate-700">
              <Plus size={21} />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">Create Contract</h2>

              <p className="text-sm text-slate-500">
                Create contract metadata manually.
              </p>
            </div>
          </div>

          <form onSubmit={handleCreateContract} className="space-y-4">
            <div>
              <label
                htmlFor="contractId"
                className="mb-1.5 block text-sm font-medium text-slate-700"
              >
                Contract ID
              </label>

              <input
                id="contractId"
                type="text"
                value={contractId}
                onChange={(event) => setContractId(event.target.value)}
                placeholder="CNT-001"
                required
                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
              />
            </div>

            <div>
              <label
                htmlFor="name"
                className="mb-1.5 block text-sm font-medium text-slate-700"
              >
                Contract Name
              </label>

              <input
                id="name"
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Software Services Agreement"
                required
                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
              />
            </div>

            <div>
              <label
                htmlFor="description"
                className="mb-1.5 block text-sm font-medium text-slate-700"
              >
                Description
              </label>

              <textarea
                id="description"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Brief contract description..."
                rows={3}
                className="w-full resize-none rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="startDate"
                  className="mb-1.5 block text-sm font-medium text-slate-700"
                >
                  Start Date
                </label>

                <div className="relative">
                  <Calendar
                    size={17}
                    className="absolute left-3 top-3 text-slate-400"
                  />

                  <input
                    id="startDate"
                    type="date"
                    value={startDate}
                    onChange={(event) => setStartDate(event.target.value)}
                    className="w-full rounded-lg border border-slate-300 py-2.5 pl-10 pr-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                  />
                </div>
              </div>

              <div>
                <label
                  htmlFor="endDate"
                  className="mb-1.5 block text-sm font-medium text-slate-700"
                >
                  End Date
                </label>

                <div className="relative">
                  <Calendar
                    size={17}
                    className="absolute left-3 top-3 text-slate-400"
                  />

                  <input
                    id="endDate"
                    type="date"
                    value={endDate}
                    onChange={(event) => setEndDate(event.target.value)}
                    className="w-full rounded-lg border border-slate-300 py-2.5 pl-10 pr-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                  />
                </div>
              </div>
            </div>

            {createError && (
              <p className="text-sm text-red-600">{createError}</p>
            )}

            {createSuccess && (
              <p className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
                {createSuccess}
              </p>
            )}

            <button
              type="submit"
              disabled={creating}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {creating ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Plus size={18} />
                  Create Contract
                </>
              )}
            </button>
          </form>
        </section>
      </div>

      {/* Contract List */}
      <section className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900">
              Existing Contracts
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              {contracts.length} contract
              {contracts.length === 1 ? "" : "s"} in the system
            </p>
          </div>
        </div>

        {contracts.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-16 text-center">
            <FileText size={40} className="mx-auto mb-4 text-slate-300" />

            <h3 className="font-semibold text-slate-800">No contracts found</h3>

            <p className="mt-1 text-sm text-slate-500">
              Upload or create your first contract to get started.
            </p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="divide-y divide-slate-100">
              {contracts.map((contract) => {
                const status = getStatusConfig(contract.status);

                return (
                  <div
                    key={contract.id}
                    className="flex flex-col gap-4 p-5 transition hover:bg-slate-50 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div className="flex min-w-0 items-start gap-4">
                      <div className="rounded-lg bg-indigo-50 p-3 text-indigo-600">
                        <FileText size={21} />
                      </div>

                      <div className="min-w-0">
                        <h3 className="truncate font-semibold text-slate-900">
                          {contract.name}
                        </h3>

                        <p className="mt-1 text-xs text-slate-500">
                          ID: {contract.contract_id}
                        </p>

                        {contract.original_filename && (
                          <p className="mt-1 truncate text-xs text-slate-500">
                            File: {contract.original_filename}
                          </p>
                        )}

                        <div className="mt-3 flex flex-wrap items-center gap-2">
                          <span
                            className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${status.className}`}
                          >
                            {status.icon}
                            {status.label}
                          </span>

                          {processingIds.includes(contract.contract_id) && (
                            <span className="inline-flex items-center gap-1 text-xs text-slate-500">
                              <Loader2 size={13} className="animate-spin" />
                              Processing document...
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <Link
                      to={`/contracts/${contract.contract_id}`}
                      className="inline-flex shrink-0 items-center justify-center gap-1 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-50"
                    >
                      View Details
                      <ChevronRight size={16} />
                    </Link>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

export default Contracts;
