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
            "status": "REVIEW",
            "confidence": 0.88,
            "margin": 0.08,
            "candidate": "SET_demo_001",
            "candidates": [
                {
                    "settlement_id": "SET_demo_001",
                    "score": 0.88,
                    "reference_similarity": 0.92,
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

    print(
        "\nFineOBS Verification Result"
    )

    print(
        "============================"
    )

    print(
        result.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    main()