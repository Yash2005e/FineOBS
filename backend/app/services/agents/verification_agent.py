from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv

from backend.app.schemas.ai_decision import (
    AIVerificationDecision,
)

load_dotenv()


class FinanceVerificationAgent:
    """
    FineOBS verification layer.

    Behavior:

    - If OPENAI_API_KEY exists:
        use OpenAI structured output.

    - If no API key exists:
        use a deterministic local fallback.

    This keeps the FineOBS pipeline usable without
    paid API access during development.
    """

    def __init__(self) -> None:

        self.api_key = os.getenv(
            "OPENAI_API_KEY"
        )

        self.model = os.getenv(
            "FINEOBS_AI_MODEL",
            "gpt-5.6-luna",
        )

        self.client = None

        if self.api_key:
            try:
                from openai import OpenAI

                self.client = OpenAI(
                    api_key=self.api_key
                )

            except ImportError:
                self.client = None

    def verify(
        self,
        evidence: dict[str, Any],
    ) -> AIVerificationDecision:

        if self.client is not None:
            return self._verify_with_openai(
                evidence
            )

        return self._verify_locally(
            evidence
        )

    # --------------------------------------------------
    # Local fallback
    # --------------------------------------------------

    def _verify_locally(
        self,
        evidence: dict[str, Any],
    ) -> AIVerificationDecision:

        matching = evidence.get(
            "matching",
            {},
        )

        discrepancy = evidence.get(
            "discrepancy",
            {},
        )

        confidence = float(
            matching.get(
                "confidence",
                0.0,
            )
        )

        margin = float(
            matching.get(
                "margin",
                0.0,
            )
        )

        settlement = evidence.get(
            "settlement"
        )

        # No candidate settlement.
        if settlement is None:

            return AIVerificationDecision(
                decision="UNRESOLVED",
                exception_type=(
                    "missing_settlement"
                ),
                confidence=min(
                    confidence,
                    0.99,
                ),
                explanation=(
                    "No settlement record provides "
                    "sufficient evidence for safe "
                    "reconciliation."
                ),
                evidence=[
                    "No settlement candidate exists."
                ],
                recommended_action=(
                    "Send to finance review queue."
                ),
            )

        amount_difference = float(
            discrepancy.get(
                "amount_difference",
                0.0,
            )
        )

        # Strong candidate with strong separation.
        if (
            confidence >= 0.95
            and margin >= 0.10
            and abs(amount_difference) <= 0.01
        ):

            return AIVerificationDecision(
                decision="AUTO_RECONCILE",
                exception_type="none",
                confidence=confidence,
                explanation=(
                    "Candidate has strong matching "
                    "confidence and sufficient "
                    "separation from alternatives."
                ),
                evidence=[
                    (
                        f"Candidate confidence: "
                        f"{confidence:.2%}"
                    ),
                    (
                        f"Candidate margin: "
                        f"{margin:.2%}"
                    ),
                    (
                        "Payment and settlement "
                        "amounts agree."
                    ),
                ],
                recommended_action=(
                    "Automatically reconcile."
                ),
            )

        # Plausible candidate, but not safe enough.
        if (
            confidence >= 0.80
            and margin >= 0.05
        ):

            return AIVerificationDecision(
                decision="HUMAN_REVIEW",
                exception_type="ambiguous_match",
                confidence=confidence,
                explanation=(
                    "A plausible settlement "
                    "candidate exists, but the "
                    "evidence is not strong enough "
                    "for autonomous reconciliation."
                ),
                evidence=[
                    (
                        f"Candidate confidence: "
                        f"{confidence:.2%}"
                    ),
                    (
                        f"Candidate margin: "
                        f"{margin:.2%}"
                    ),
                ],
                recommended_action=(
                    "Require finance reviewer approval."
                ),
            )

        return AIVerificationDecision(
            decision="UNRESOLVED",
            exception_type="insufficient_evidence",
            confidence=confidence,
            explanation=(
                "Available evidence is insufficient "
                "to safely determine the correct "
                "settlement."
            ),
            evidence=[
                (
                    f"Candidate confidence: "
                    f"{confidence:.2%}"
                ),
                (
                    f"Candidate margin: "
                    f"{margin:.2%}"
                ),
            ],
            recommended_action=(
                "Keep unresolved and escalate."
            ),
        )

    # --------------------------------------------------
    # Optional OpenAI implementation
    # --------------------------------------------------

    def _verify_with_openai(
        self,
        evidence: dict[str, Any],
    ) -> AIVerificationDecision:

        system_prompt = """
You are the financial verification agent
inside FineOBS.

You verify reconciliation proposals.

Rules:

1. Never invent financial facts.
2. Never hide discrepancies.
3. AUTO_RECONCILE only when evidence is strong.
4. Ambiguous cases require HUMAN_REVIEW.
5. Insufficient evidence must remain UNRESOLVED.
6. Use only the supplied evidence.
7. Be conservative with financial decisions.
"""

        response = self.client.responses.parse(
            model=self.model,
            instructions=system_prompt,
            input=json.dumps(
                evidence,
                default=str,
            ),
            text_format=AIVerificationDecision,
        )

        parsed = response.output_parsed

        if parsed is None:
            raise RuntimeError(
                "OpenAI returned no structured decision."
            )

        return parsed