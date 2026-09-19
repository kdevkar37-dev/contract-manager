// import { FormEvent, useEffect, useState } from "react";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";

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

  async function loadContracts() {
    try {
      setError("");

      const data = await getContracts();

      setContracts(data);

      const activeProcessingIds = data
        .filter((contract) => contract.status === "processing")
        .map((contract) => contract.contract_id);

      setProcessingIds(activeProcessingIds);
    } catch {
      setError("Failed to load contracts.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadContracts();
  }, []);

  useEffect(() => {
    if (processingIds.length === 0) {
      return;
    }

    const interval = window.setInterval(async () => {
      for (const contractId of processingIds) {
        try {
          const document = await getContractDocumentStatus(contractId);

          setContracts((currentContracts) =>
            currentContracts.map((contract) =>
              contract.contract_id === contractId
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
              currentIds.filter((id) => id !== contractId),
            );
          }
        } catch {
          // Continue polling if the status request temporarily fails.
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
        contract_id: contractId,
        name,
        description: description || undefined,
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
    } catch {
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
    } catch {
      setUploadError(
        "Failed to upload contract. Please check the file and try again.",
      );
    } finally {
      setUploading(false);
    }
  }

  if (loading) {
    return <h1>Loading contracts...</h1>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  return (
    <div>
      <h1>Contracts</h1>

      <section>
        <h2>Upload Contract</h2>

        <form onSubmit={handleUploadContract}>
          <div>
            <label htmlFor="contractFile">Contract File</label>

            <input
              id="contractFile"
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(event) =>
                setSelectedFile(event.target.files?.[0] ?? null)
              }
            />
          </div>

          <button type="submit" disabled={uploading}>
            {uploading ? "Uploading..." : "Upload Contract"}
          </button>
        </form>

        {uploadSuccess && <p>{uploadSuccess}</p>}

        {uploadError && <p>{uploadError}</p>}
      </section>

      <hr />

      <section>
        <h2>Create Contract Manually</h2>

        <form onSubmit={handleCreateContract}>
          <div>
            <label htmlFor="contractId">Contract ID</label>

            <input
              id="contractId"
              type="text"
              value={contractId}
              onChange={(event) => setContractId(event.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="name">Contract Name</label>

            <input
              id="name"
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="description">Description</label>

            <textarea
              id="description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
          </div>

          <div>
            <label htmlFor="startDate">Start Date</label>

            <input
              id="startDate"
              type="date"
              value={startDate}
              onChange={(event) => setStartDate(event.target.value)}
            />
          </div>

          <div>
            <label htmlFor="endDate">End Date</label>

            <input
              id="endDate"
              type="date"
              value={endDate}
              onChange={(event) => setEndDate(event.target.value)}
            />
          </div>

          <button type="submit" disabled={creating}>
            {creating ? "Creating..." : "Create Contract"}
          </button>
        </form>

        {createSuccess && <p>{createSuccess}</p>}

        {createError && <p>{createError}</p>}
      </section>

      <hr />

      <section>
        <h2>Existing Contracts</h2>

        {contracts.length === 0 ? (
          <p>No contracts found.</p>
        ) : (
          <div>
            {contracts.map((contract) => (
              <div key={contract.id}>
                <h3>{contract.name}</h3>

                <p>Contract ID: {contract.contract_id}</p>

                <p>
                  Status:{" "}
                  {contract.status === "completed"
                    ? "Completed"
                    : contract.status === "failed"
                      ? "Failed"
                      : contract.status === "processing"
                        ? "Processing..."
                        : contract.status}
                </p>

                {contract.original_filename && (
                  <p>File: {contract.original_filename}</p>
                )}

                <Link to={`/contracts/${contract.contract_id}`}>
                  Open Contract
                </Link>

                <hr />
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Contracts;
