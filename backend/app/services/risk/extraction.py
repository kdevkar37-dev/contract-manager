import json
from dataclasses import dataclass

from ai.rag.llm import ContractLLMService


@dataclass
class ExtractedRisk:
    risk_type: str
    severity: str
    title: str
    description: str
    evidence: str | None = None
    source: str | None = None
    confidence: str | None = None


class RiskExtractionService:
    """
    Extracts structured contract risks using the LLM.

    The LLM identifies and explains risks.
    It does not calculate financial values or decision scores.
    """

    def __init__(
        self,
        llm_service: ContractLLMService | None = None,
    ):
        self.llm_service = (
            llm_service or ContractLLMService()
        )

    def extract(
        self,
        contract_text: str,
    ) -> list[ExtractedRisk]:
        if not contract_text.strip():
            return []

        prompt = self._build_prompt(contract_text)

        response = self.llm_service.invoke(prompt)

        return self._parse_response(response)

    @staticmethod
    def _build_prompt(
        contract_text: str,
    ) -> str:
        return f"""
You are a contract risk analysis assistant.

Analyze ONLY the contract text provided below.

Identify meaningful risks that could affect the organization.

Look specifically for:
- Financial risks
- Payment risks
- Penalty risks
- Liability risks
- Termination risks
- Renewal risks
- Legal or compliance risks
- Operational risks
- Dependency risks
- Missing or uncertain information

For every identified risk, return:

- risk_type
- severity
- title
- description
- evidence
- source
- confidence

Severity must be one of:
low
medium
high
critical

Return ONLY valid JSON.

The JSON must be an array in this format:

[
  {{
    "risk_type": "financial",
    "severity": "high",
    "title": "Example risk",
    "description": "Explanation of the risk.",
    "evidence": "Relevant contract wording.",
    "source": "Contract Section 5",
    "confidence": "0.90"
  }}
]

If no meaningful risks are found, return:

[]

Do not invent contract information.

Contract Text:
----------------
{contract_text}
----------------
"""

    @staticmethod
    def _parse_response(
        response: str,
    ) -> list[ExtractedRisk]:
        if not response.strip():
            return []

        cleaned_response = response.strip()

        if cleaned_response.startswith("```"):
            cleaned_response = (
                cleaned_response
                .replace("```json", "", 1)
                .replace("```", "")
                .strip()
            )

        try:
            data = json.loads(cleaned_response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Risk extraction returned invalid JSON."
            ) from exc

        if not isinstance(data, list):
            raise ValueError(
                "Risk extraction response must be a JSON array."
            )

        risks: list[ExtractedRisk] = []

        for item in data:
            if not isinstance(item, dict):
                continue

            risk_type = item.get("risk_type")
            severity = item.get("severity")
            title = item.get("title")
            description = item.get("description")

            if not all(
                [
                    risk_type,
                    severity,
                    title,
                    description,
                ]
            ):
                continue

            risks.append(
                ExtractedRisk(
                    risk_type=str(risk_type),
                    severity=str(severity).lower(),
                    title=str(title),
                    description=str(description),
                    evidence=(
                        str(item["evidence"])
                        if item.get("evidence") is not None
                        else None
                    ),
                    source=(
                        str(item["source"])
                        if item.get("source") is not None
                        else None
                    ),
                    confidence=(
                        str(item["confidence"])
                        if item.get("confidence") is not None
                        else None
                    ),
                )
            )

        return risks