from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ai.rag.llm import ContractLLMService


class ContractInformationExtractionResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    client_name: str | None = None
    vendor_name: str | None = None

    contract_value: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )

    currency: str | None = None
    payment_terms: str | None = None
    renewal_terms: str | None = None
    termination_terms: str | None = None

    obligations: list[str] = Field(
        default_factory=list,
    )

    dependencies: list[str] = Field(
        default_factory=list,
    )

    @field_validator(
        "contract_value",
        mode="before",
    )
    @classmethod
    def validate_contract_value(cls, value):
        if value is None or value == "":
            return None

        try:
            return Decimal(str(value))
        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ) as exc:
            raise ValueError(
                "contract_value must be a valid numeric value."
            ) from exc

    @field_validator(
        "obligations",
        "dependencies",
        mode="before",
    )
    @classmethod
    def normalize_list_fields(cls, value):
        if value is None:
            return []

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return []

            return [value]

        if isinstance(value, list):
            return value

        raise ValueError(
            "Expected a list or null value."
        )


@dataclass(frozen=True)
class ExtractedContractInformation:
    client_name: str | None
    vendor_name: str | None
    contract_value: Decimal | None
    currency: str | None
    payment_terms: str | None
    renewal_terms: str | None
    termination_terms: str | None
    obligations: list[str]
    dependencies: list[str]


class ContractInformationExtractionService:
    def __init__(
        self,
        llm_service: ContractLLMService | None = None,
    ):
        self.llm_service = (
            llm_service
            if llm_service is not None
            else ContractLLMService()
        )

    def extract(
        self,
        contract_text: str,
    ) -> ExtractedContractInformation:

        if not contract_text or not contract_text.strip():
            raise ValueError(
                "Contract text cannot be empty."
            )

        prompt = f"""
Extract structured contract information from the contract below.

Rules:
- Extract ONLY information explicitly stated in the contract.
- Do NOT calculate or infer values.
- If information is not present, return null.
- For obligations, return [] when none are explicitly stated.
- For dependencies, return [] when none are explicitly stated.
- Do NOT treat financial calculations as contract values.
- contract_value must be the explicitly stated total contract/commercial value.
- contract_value must be a numeric value only, without currency symbols.
- currency must contain the explicitly stated currency code or symbol.
- Keep obligations and dependencies as concise factual items.
- Do not invent parties, values, terms, obligations, or dependencies.
- Return ONLY valid JSON.
- Use double quotes for every JSON key and string.
- Do NOT use trailing commas.
- Do not include markdown or explanations.

Required JSON fields:

client_name
vendor_name
contract_value
currency
payment_terms
renewal_terms
termination_terms
obligations
dependencies

Contract:
{contract_text}
"""

        raw_response = self.llm_service.invoke(prompt)

        data = self._parse_json(raw_response)

        result = ContractInformationExtractionResult.model_validate(
            data
        )

        return ExtractedContractInformation(
            client_name=result.client_name,
            vendor_name=result.vendor_name,
            contract_value=result.contract_value,
            currency=result.currency,
            payment_terms=result.payment_terms,
            renewal_terms=result.renewal_terms,
            termination_terms=result.termination_terms,
            obligations=list(result.obligations),
            dependencies=list(result.dependencies),
        )

    @staticmethod
    def _parse_json(value: str) -> dict:

        if not isinstance(value, str):
            raise ValueError(
                "LLM response must be a string."
            )

        text = value.strip()

        if not text:
            raise ValueError(
                "LLM returned an empty response."
            )

        # ---------------------------------------------------------
        # Remove markdown code fences
        # ---------------------------------------------------------

        if text.startswith("```"):
            lines = text.splitlines()

            if (
                lines
                and lines[0].strip().startswith("```")
            ):
                lines = lines[1:]

            if (
                lines
                and lines[-1].strip() == "```"
            ):
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        # ---------------------------------------------------------
        # First attempt: strict JSON
        # ---------------------------------------------------------

        try:
            parsed = json.loads(text)

        except json.JSONDecodeError:

            # -----------------------------------------------------
            # Second attempt:
            # Extract the JSON object if the LLM added
            # surrounding explanation.
            # -----------------------------------------------------

            start = text.find("{")
            end = text.rfind("}")

            if start == -1 or end == -1 or end <= start:
                raise ValueError(
                    "LLM returned invalid JSON."
                )

            candidate = text[start : end + 1]

            # -----------------------------------------------------
            # Remove trailing commas before } or ]
            #
            # Example:
            # {
            #     "currency": "INR",
            # }
            #
            # becomes:
            # {
            #     "currency": "INR"
            # }
            # -----------------------------------------------------

            candidate = re.sub(
                r",\s*([}\]])",
                r"\1",
                candidate,
            )

            try:
                parsed = json.loads(candidate)

            except json.JSONDecodeError as exc:
                raise ValueError(
                    "LLM returned invalid JSON."
                ) from exc

        if not isinstance(parsed, dict):
            raise ValueError(
                "LLM response must be a JSON object."
            )

        return parsed