from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence


@dataclass(frozen=True)
class ContractComparisonInput:
    contract_id: str
    contract_value: Decimal | None


@dataclass(frozen=True)
class ContractComparisonResult:
    contract_id: str
    contract_value: Decimal | None
    contract_value_score: Decimal | None
    rank: int | None


class ContractComparisonService:
    """
    Deterministically compares contracts using their explicitly
    stored contract values.

    Contract-value score:
        (contract value / maximum contract value) * 100

    Therefore:
        Highest contract value = 100
        Other contracts = proportional score

    Contracts without a known contract value are not scored.
    """

    def compare(
        self,
        contracts: Sequence[ContractComparisonInput],
    ) -> list[ContractComparisonResult]:

        if not contracts:
            return []

        valid_values = [
            contract.contract_value
            for contract in contracts
            if contract.contract_value is not None
            and contract.contract_value >= Decimal("0")
        ]

        if not valid_values:
            return [
                ContractComparisonResult(
                    contract_id=contract.contract_id,
                    contract_value=contract.contract_value,
                    contract_value_score=None,
                    rank=None,
                )
                for contract in contracts
            ]

        maximum_value = max(valid_values)

        results: list[ContractComparisonResult] = []

        for contract in contracts:

            if (
                contract.contract_value is None
                or contract.contract_value < Decimal("0")
                or maximum_value == Decimal("0")
            ):
                score = None
            else:
                score = (
                    contract.contract_value
                    / maximum_value
                    * Decimal("100")
                ).quantize(Decimal("0.0001"))

            results.append(
                ContractComparisonResult(
                    contract_id=contract.contract_id,
                    contract_value=contract.contract_value,
                    contract_value_score=score,
                    rank=None,
                )
            )

        # Rank only contracts that have a calculated score.
        ranked_indexes = sorted(
            range(len(results)),
            key=lambda index: (
                results[index].contract_value_score
                if results[index].contract_value_score is not None
                else Decimal("-1")
            ),
            reverse=True,
        )

        ranks: dict[int, int] = {}
        current_rank = 0
        previous_score: Decimal | None = None

        for position, index in enumerate(ranked_indexes, start=1):

            score = results[index].contract_value_score

            if score is None:
                continue

            if score != previous_score:
                current_rank = position
                previous_score = score

            ranks[index] = current_rank

        return [
            ContractComparisonResult(
                contract_id=result.contract_id,
                contract_value=result.contract_value,
                contract_value_score=result.contract_value_score,
                rank=ranks.get(index),
            )
            for index, result in enumerate(results)
        ]