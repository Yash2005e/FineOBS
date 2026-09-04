from pprint import pprint

from backend.app.services.agents.verification_agent import (
    FinanceVerificationAgent,
)


def main() -> None:

    agent = FinanceVerificationAgent()

    evidence = {
        "payment": {
            "payment_id": "pay_demo_001",
            "order_id": "ORD00100",
            "customer_id": "CUST001",
            "amount": 8500.00,
            "payment_date": "2026-08-10",
            "payment_method": "upi",
        },
        "matching": {
            "status": "HIGH_CONFIDENCE",
            "confidence": 0.986,
            "candidate": "SET_demo_001",
            "top_candidates": [
                {
                    "settlement_id": "SET_demo_001",
                    "score": 0.986,
                    "reference_similarity": 1.0,
                    "amount_similarity": 1.0,
                    "customer_similarity": 1.0,
                    "date_similarity": 0.86,
                }
            ],
        },
        "settlement": {
            "settlement_id": "SET_demo_001",
            "payment_id": "pay_demo_001",
            "merchant_reference": "ORD00100",
            "customer_id": "CUST001",
            "gross_amount": 8500.00,
            "fee": 170.00,
            "tax": 30.60,
            "net_amount": 8299.40,
            "settlement_date": "2026-08-11",
        },
        "discrepancy": {
            "amount_difference": 0.0,
            "settlement_delay_days": 1,
        },
    }

    result = agent.verify(
        evidence
    )

    print("\nFineOBS AI Verification")
    print("======================")

    pprint(
        result.model_dump(),
        sort_dicts=False,
    )


if __name__ == "__main__":
    main()