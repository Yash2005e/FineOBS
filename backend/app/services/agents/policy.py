from backend.app.schemas.ai_decision import (
    AIVerificationDecision,
)


def apply_financial_policy(
    decision: AIVerificationDecision,
) -> AIVerificationDecision:

    # Never allow autonomous action
    # below the strict confidence threshold.
    if (
        decision.decision
        == "AUTO_RECONCILE"
        and decision.confidence < 0.95
    ):
        decision.decision = "HUMAN_REVIEW"

        decision.recommended_action = (
            "Human approval required because "
            "confidence is below the autonomous "
            "resolution threshold."
        )

    # Very low confidence must remain unresolved.
    if (
        decision.confidence < 0.80
        and decision.decision
        == "AUTO_RECONCILE"
    ):
        decision.decision = "UNRESOLVED"

        decision.recommended_action = (
            "Insufficient confidence for "
            "financial automation."
        )

    return decision