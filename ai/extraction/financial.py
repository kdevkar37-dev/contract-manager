import json
import re
from decimal import Decimal

from pydantic import BaseModel, Field

from ai.rag.llm import ContractLLMService
from backend.app.services.financial.engine import FinancialInputs


class FinancialExtractionResult(BaseModel):
    revenue: Decimal | None = None
    initial_investment: Decimal | None = None
    fixed_costs: Decimal | None = None
    variable_costs: Decimal | None = None
    contribution_margin: Decimal | None = None

    assumptions: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


FINANCIAL_EXTRACTION_PROMPT = """
You are a financial information extraction assistant.

Extract ONLY financial information explicitly stated in the
contract text.

Do NOT calculate any values.

Do NOT infer missing values.

If a value is not explicitly available, return null.

Extract these fields:

- revenue
- initial_investment
- fixed_costs
- variable_costs
- contribution_margin
- assumptions
- sources

Rules:

1. Return ONLY valid JSON.
2. Use numbers without currency symbols or commas.
3. Do not calculate profit.
4. Do not calculate ROI.
5. Do not calculate profit margin.
6. Do not calculate break-even.
7. Only extract values explicitly present in the contract.
8. Put relevant contract statements or section references in sources.
9. Put clearly stated assumptions in assumptions.
10. If information is missing, use null.

Expected JSON format:

{{
  "revenue": null,
  "initial_investment": null,
  "fixed_costs": null,
  "variable_costs": null,
  "contribution_margin": null,
  "assumptions": [],
  "sources": []
}}

Contract Text:
{contract_text}
"""


class FinancialExtractionService:
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
    ) -> FinancialInputs:
        if not contract_text.strip():
            raise ValueError(
                "Contract text cannot be empty."
            )

        prompt = FINANCIAL_EXTRACTION_PROMPT.format(
            contract_text=contract_text
        )

        response = self.llm_service.invoke(prompt)

        data = self._parse_json(response)

        result = FinancialExtractionResult.model_validate(data)

        return FinancialInputs(
            revenue=result.revenue,
            initial_investment=result.initial_investment,
            fixed_costs=result.fixed_costs,
            variable_costs=result.variable_costs,
            contribution_margin=result.contribution_margin,
            assumptions=result.assumptions,
            sources=result.sources,
        )

    @staticmethod
    def _parse_json(response: str) -> dict:
        cleaned = response.strip()

        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
        )

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid JSON for financial extraction."
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                "Financial extraction response must be a JSON object."
            )

        return data