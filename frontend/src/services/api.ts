import { apiClient } from "./apiClient";

export interface Contract {
  id: number;
  contract_id: string;
  name: string;
  description: string | null;
  start_date: string | null;
  end_date: string | null;
  source_type: string;
  original_filename: string | null;
  mime_type: string | null;
  storage_key: string | null;
  status: string;
}

export interface ContractCreate {
  contract_id: string;
  name: string;
  description?: string;
  start_date?: string;
  end_date?: string;
}

export interface ContractDocumentStatus {
  contract_id: string;
  document_id: number;
  processing_status: string;
  extracted_text: string | null;
  processed_at: string | null;
  error_message: string | null;
}

export interface ContractUploadResponse {
  message: string;
  contract_id: string;
  name: string;
  filename: string;
  content_type: string;
  storage_key: string;
  status: string;
}

export interface ContractAskRequest {
  question: string;
}

export interface ContractSource {
  document_id: number;
  chunk_index: number;
  evidence: string;
}

export interface ContractAskResponse {
  contract_id: string;
  question: string;
  answer: string;
  sources: ContractSource[];
}

/* ---------------------------------------------------------
   Financial Analysis
--------------------------------------------------------- */

export interface FinancialAnalysis {
  contract_id: string;
  revenue: string | null;
  initial_investment: string | null;
  fixed_costs: string | null;
  variable_costs: string | null;
  total_cost: string | null;
  profit: string | null;
  roi: string | null;
  profit_margin: string | null;
  break_even: string | null;
  assumptions: string[];
  sources: string[];
}

/* ---------------------------------------------------------
   Risk Analysis
--------------------------------------------------------- */

export interface RiskAnalysis {
  id: number;
  contract_id: string;
  risk_type: string;
  severity: string;
  title: string;
  description: string;
  evidence: string | null;
  source: string | null;
  confidence: string | null;
}

/* ---------------------------------------------------------
   Contract Information
--------------------------------------------------------- */

export interface ContractInformation {
  contract_id: string;
  client_name: string | null;
  vendor_name: string | null;
  contract_value: number | null;
  currency: string | null;
  payment_terms: string | null;
  renewal_terms: string | null;
  termination_terms: string | null;
  obligations: string[];
  dependencies: string[];
  created_at: string;
  updated_at: string;
}

/* ---------------------------------------------------------
   Contract Comparison
--------------------------------------------------------- */

export interface ContractComparison {
  contract_id: string;
  contract_value: number | null;
  contract_value_score: number | null;
  rank: number | null;
}

export interface ContractComparisonResponse {
  count: number;
  contracts: ContractComparison[];
}

/* ---------------------------------------------------------
   Decision Score
--------------------------------------------------------- */

export interface DecisionScore {
  contract_id: string;
  score: number | null;
  financial_score: number | null;
  risk_score: number | null;
  contract_value_score: number | null;
  financial_weight?: number | null;
  risk_weight?: number | null;
  contract_value_weight?: number | null;
  explanation: string | null;
}

/* ---------------------------------------------------------
   Recommendation
--------------------------------------------------------- */

export interface ContractRecommendation {
  contract_id: string;
  contract_name: string | null;
  contract_value: number | null;
  final_score: number | null;
  rank: number | null;
  financial_score: number | null;
  risk_score: number | null;
  contract_value_score: number | null;
  explanation: string | null;
}

export interface ContractRecommendationResponse {
  count: number;
  recommendations: ContractRecommendation[];
}

/* ---------------------------------------------------------
   Decision Workflow
--------------------------------------------------------- */

export interface DecisionWorkflowResponse {
  contracts_processed: number;
  recommendations_count: number;
  top_recommendation: ContractRecommendation | null;
  recommendations: ContractRecommendation[];
}

/* ---------------------------------------------------------
   Health
--------------------------------------------------------- */

export function healthCheck() {
  return apiClient("/health");
}

/* ---------------------------------------------------------
   Contracts
--------------------------------------------------------- */

export function getContracts(): Promise<Contract[]> {
  return apiClient("/contracts/");
}

export function getContract(contractId: string): Promise<Contract> {
  return apiClient(`/contracts/${contractId}`);
}

export function createContract(contract: ContractCreate): Promise<Contract> {
  return apiClient("/contracts/", {
    method: "POST",
    body: JSON.stringify(contract),
  });
}

/* ---------------------------------------------------------
   Contract Intake
--------------------------------------------------------- */

export function uploadContract(file: File): Promise<ContractUploadResponse> {
  const formData = new FormData();

  formData.append("file", file);

  return apiClient("/intake/upload", {
    method: "POST",
    body: formData,
  });
}

/* ---------------------------------------------------------
   Contract Document
--------------------------------------------------------- */

export function getContractDocumentStatus(
  contractId: string,
): Promise<ContractDocumentStatus> {
  return apiClient(`/contracts/${contractId}/document`);
}

/* ---------------------------------------------------------
   Contract RAG / Q&A
--------------------------------------------------------- */

export function askContract(
  contractId: string,
  question: string,
): Promise<ContractAskResponse> {
  return apiClient(`/contracts/${contractId}/ask`, {
    method: "POST",
    body: JSON.stringify({
      question,
    } satisfies ContractAskRequest),
  });
}

/* ---------------------------------------------------------
   Financial Analysis
--------------------------------------------------------- */

export function getFinancialAnalysis(
  contractId: string,
): Promise<FinancialAnalysis> {
  return apiClient(`/contracts/${contractId}/financial-analysis`);
}

/* ---------------------------------------------------------
   Risk Analysis
--------------------------------------------------------- */

export function getContractRisks(contractId: string): Promise<RiskAnalysis[]> {
  return apiClient(`/contracts/${contractId}/risks`);
}

/* ---------------------------------------------------------
   Contract Information
--------------------------------------------------------- */

export function getContractInformation(
  contractId: string,
): Promise<ContractInformation> {
  return apiClient(`/contracts/${contractId}/information`);
}

/* ---------------------------------------------------------
   Contract Comparison
--------------------------------------------------------- */

export function getContractComparison(): Promise<ContractComparisonResponse> {
  return apiClient("/contracts/comparison");
}

/* ---------------------------------------------------------
   Automatic Decision Score
--------------------------------------------------------- */

export function calculateAutomaticDecisionScore(
  contractId: string,
): Promise<DecisionScore> {
  return apiClient(`/contracts/${contractId}/decision-score/automatic`, {
    method: "POST",
  });
}

/* ---------------------------------------------------------
   Combined Decision
--------------------------------------------------------- */

export interface CombinedDecisionResponse {
  count: number;
  contracts: DecisionScore[];
}

export function runCombinedDecision(): Promise<CombinedDecisionResponse> {
  return apiClient("/contracts/decision/automatic", {
    method: "POST",
  });
}

/* ---------------------------------------------------------
   Recommendations
--------------------------------------------------------- */

export function getRecommendations(): Promise<ContractRecommendationResponse> {
  return apiClient("/contracts/recommendation");
}

/* ---------------------------------------------------------
   Complete Decision Workflow
--------------------------------------------------------- */

export function runDecisionWorkflow(): Promise<DecisionWorkflowResponse> {
  return apiClient("/contracts/decision/workflow", {
    method: "POST",
  });
}
