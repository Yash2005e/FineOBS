from pathlib import Path

import pandas as pd

from backend.app.services.matching.matcher import (
    SettlementMatcher,
)


ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "generated"


def main() -> None:

    payments = pd.read_csv(
        DATA_DIR / "payments.csv"
    )

    settlements = pd.read_csv(
        DATA_DIR / "settlements.csv"
    )

    payments["payment_date"] = pd.to_datetime(
        payments["payment_date"]
    )

    settlements["settlement_date"] = pd.to_datetime(
        settlements["settlement_date"]
    )

    matcher = SettlementMatcher(
        settlements
    )

    print("\nFineOBS Intelligent Matcher")
    print("===========================\n")

    for index in [0, 10, 20, 30, 40]:

        payment = payments.iloc[index]

        result = matcher.match(payment)

        print(
            f"Payment: {payment['payment_id']}"
        )

        print(
            f"Order:   {payment['order_id']}"
        )

        print(
            f"Result:  {result['status']}"
        )

        print(
            f"Confidence: "
            f"{result['confidence']:.2%}"
        )

        print(
            f"Best settlement: "
            f"{result['candidate']}"
        )

        print(
            "\nTop candidates:"
        )

        for candidate in result["candidates"][:3]:
            print(
                f"  {candidate['settlement_id']} "
                f"| score={candidate['score']:.3f} "
                f"| ref={candidate['reference_similarity']:.3f} "
                f"| amount={candidate['amount_similarity']:.3f} "
                f"| customer={candidate['customer_similarity']:.3f}"
            )

        print("\n" + "-" * 70)


if __name__ == "__main__":
    main()