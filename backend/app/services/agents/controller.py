from __future__ import annotations

import pandas as pd

from backend.app.schemas.ai_decision import (
    AIVerificationDecision,
)
from backend.app.services.agents.evidence import (
    build_verification_evidence,
)
from backend.app.services.agents.policy import (
    apply_financial_policy,
)
from backend.app.services.agents.verification_agent import (
    FinanceVerificationAgent,
)


class FinanceController:

    def __init__(self) -> None:
        self.agent = FinanceVerificationAgent()

    def verify_case(
        self,
        payment: pd.Series,
        settlement: pd.Series | None,
        match_result: dict,
    ) -> dict:

        evidence = build_verification_evidence(
            payment=payment,
            settlement=settlement,
            match_result=match_result,
        )

        decision = self.agent.verify(
            evidence
        )

        decision = apply_financial_policy(
            decision
        )

        return {
            "evidence": evidence,
            "decision": decision,
        }