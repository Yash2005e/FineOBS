from __future__ import annotations

import pandas as pd


def build_verification_evidence(
    payment: pd.Series,
    settlement: pd.Series | None,
    match_result: dict,
) -> dict:

    evidence = {
        "payment": {
            "payment_id": payment["payment_id"],
            "order_id": payment["order_id"],
            "customer_id": payment["customer_id"],
            "amount": float(
                payment["payment_amount"]
            ),
            "payment_date": str(
                payment["payment_date"]
            ),
            "payment_method": payment[
                "payment_method"
            ],
        },
        "matching": {
            "status": match_result["status"],
            "confidence": match_result[
                "confidence"
            ],
            "candidate": match_result[
                "candidate"
            ],
            "top_candidates": match_result[
                "candidates"
            ][:3],
        },
    }

    if settlement is None:

        evidence["settlement"] = None

        evidence["discrepancy"] = {
            "type": "missing_settlement",
            "description": (
                "No settlement candidate "
                "was available."
            ),
        }

        return evidence

    payment_amount = float(
        payment["payment_amount"]
    )

    settlement_amount = float(
        settlement["gross_amount"]
    )

    difference = round(
        payment_amount - settlement_amount,
        2,
    )

    settlement_date = pd.Timestamp(
        settlement["settlement_date"]
    )

    payment_date = pd.Timestamp(
        payment["payment_date"]
    )

    settlement_delay = (
        settlement_date - payment_date
    ).days

    evidence["settlement"] = {
        "settlement_id": settlement[
            "settlement_id"
        ],
        "payment_id": settlement[
            "payment_id"
        ],
        "merchant_reference": settlement[
            "merchant_reference"
        ],
        "customer_id": settlement[
            "customer_id"
        ],
        "gross_amount": settlement_amount,
        "fee": float(
            settlement["fee"]
        ),
        "tax": float(
            settlement["tax"]
        ),
        "net_amount": float(
            settlement["net_amount"]
        ),
        "settlement_date": str(
            settlement_date
        ),
    }

    evidence["discrepancy"] = {
        "amount_difference": difference,
        "settlement_delay_days": settlement_delay,
    }

    return evidence