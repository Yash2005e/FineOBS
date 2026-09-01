from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker


SEED = 42
NUM_RECORDS = 500

random.seed(SEED)
fake = Faker()
Faker.seed(SEED)

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "generated"
GROUND_TRUTH_DIR = ROOT / "data" / "ground_truth"

DATA_DIR.mkdir(parents=True, exist_ok=True)
GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)


def random_amount() -> float:
    return round(random.uniform(100, 50000), 2)


def random_date(
    start: datetime,
    end: datetime,
) -> datetime:
    seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, seconds))


def generate_orders(n: int) -> pd.DataFrame:
    start = datetime(2026, 1, 1)
    end = datetime(2026, 8, 31)

    rows = []

    for i in range(1, n + 1):
        order_id = f"ORD{i:05d}"

        rows.append(
            {
                "order_id": order_id,
                "invoice_id": f"INV{i:05d}",
                "customer_id": f"CUST{random.randint(1, 250):04d}",
                "order_amount": random_amount(),
                "order_date": random_date(start, end),
                "currency": "INR",
                "order_status": "paid",
            }
        )

    return pd.DataFrame(rows)


def generate_payments(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for _, order in orders.iterrows():
        rows.append(
            {
                "payment_id": f"pay_{fake.uuid4()}",
                "order_id": order["order_id"],
                "customer_id": order["customer_id"],
                "payment_amount": order["order_amount"],
                "payment_status": "captured",
                "payment_date": order["order_date"],
                "payment_method": random.choice(
                    [
                        "card",
                        "upi",
                        "netbanking",
                        "wallet",
                    ]
                ),
            }
        )

    return pd.DataFrame(rows)


def generate_settlements(
    payments: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for _, payment in payments.iterrows():
        fee = round(payment["payment_amount"] * 0.02, 2)
        tax = round(fee * 0.18, 2)

        net_amount = round(
            payment["payment_amount"] - fee - tax,
            2,
        )

        settlement_date = (
            payment["payment_date"]
            + timedelta(days=random.randint(1, 3))
        )

        rows.append(
            {
                "settlement_id": f"SET_{fake.uuid4()}",
                "payment_id": payment["payment_id"],
                "gross_amount": payment["payment_amount"],
                "fee": fee,
                "tax": tax,
                "net_amount": net_amount,
                "settlement_date": settlement_date,
                "settlement_status": "settled",
            }
        )

    return pd.DataFrame(rows)


def build_ground_truth(
    payments: pd.DataFrame,
    settlements: pd.DataFrame,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "payment_id": payments["payment_id"],
            "expected_order_id": payments["order_id"],
            "expected_settlement_exists": payments[
                "payment_id"
            ].isin(settlements["payment_id"]),
            "true_status": "matched",
            "exception_type": "none",
        }
    )


def inject_exceptions(
    payments: pd.DataFrame,
    settlements: pd.DataFrame,
    ground_truth: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    # 1. Amount mismatches
    amount_indices = random.sample(
        list(range(NUM_RECORDS)),
        40,
    )

    for idx in amount_indices:
        payment_id = payments.loc[idx, "payment_id"]

        settlement_idx = settlements.index[
            settlements["payment_id"] == payment_id
        ]

        if len(settlement_idx) > 0:
            s_idx = settlement_idx[0]

            settlements.loc[s_idx, "net_amount"] = round(
                settlements.loc[s_idx, "net_amount"] - 150,
                2,
            )

            ground_truth.loc[idx, "true_status"] = "exception"
            ground_truth.loc[idx, "exception_type"] = (
                "amount_mismatch"
            )

    # 2. Missing settlements
    missing_indices = random.sample(
        [
            i for i in range(NUM_RECORDS)
            if i not in amount_indices
        ],
        30,
    )

    missing_payment_ids = payments.loc[
        missing_indices,
        "payment_id",
    ].tolist()

    settlements = settlements[
        ~settlements["payment_id"].isin(
            missing_payment_ids
        )
    ].reset_index(drop=True)

    for idx in missing_indices:
        ground_truth.loc[idx, "true_status"] = "exception"
        ground_truth.loc[idx, "exception_type"] = (
            "missing_settlement"
        )

    # 3. Duplicate settlements
    duplicate_indices = random.sample(
        [
            i
            for i in range(NUM_RECORDS)
            if i not in amount_indices
            and i not in missing_indices
        ],
        20,
    )

    duplicates = settlements[
        settlements["payment_id"].isin(
            payments.loc[
                duplicate_indices,
                "payment_id",
            ]
        )
    ].copy()

    if not duplicates.empty:
        duplicates["settlement_id"] = duplicates[
            "settlement_id"
        ].apply(lambda _: f"SET_DUP_{fake.uuid4()}")

        settlements = pd.concat(
            [settlements, duplicates],
            ignore_index=True,
        )

    for idx in duplicate_indices:
        ground_truth.loc[idx, "true_status"] = "exception"
        ground_truth.loc[idx, "exception_type"] = (
            "duplicate_settlement"
        )

    # 4. Settlement timing problems
    timing_indices = random.sample(
        [
            i
            for i in range(NUM_RECORDS)
            if i not in amount_indices
            and i not in missing_indices
            and i not in duplicate_indices
        ],
        20,
    )

    for idx in timing_indices:
        payment_id = payments.loc[idx, "payment_id"]

        settlement_idx = settlements.index[
            settlements["payment_id"] == payment_id
        ]

        if len(settlement_idx) > 0:
            s_idx = settlement_idx[0]

            settlements.loc[
                s_idx,
                "settlement_date",
            ] = (
                payments.loc[idx, "payment_date"]
                + timedelta(days=10)
            )

            ground_truth.loc[
                idx,
                "true_status",
            ] = "exception"

            ground_truth.loc[
                idx,
                "exception_type",
            ] = "settlement_delay"

    return payments, settlements, ground_truth


def main() -> None:
    print("Generating FineOBS benchmark...")

    orders = generate_orders(NUM_RECORDS)

    payments = generate_payments(orders)

    settlements = generate_settlements(payments)

    ground_truth = build_ground_truth(
        payments,
        settlements,
    )

    payments, settlements, ground_truth = inject_exceptions(
        payments,
        settlements,
        ground_truth,
    )

    orders.to_csv(
        DATA_DIR / "orders.csv",
        index=False,
    )

    payments.to_csv(
        DATA_DIR / "payments.csv",
        index=False,
    )

    settlements.to_csv(
        DATA_DIR / "settlements.csv",
        index=False,
    )

    ground_truth.to_csv(
        GROUND_TRUTH_DIR / "ground_truth.csv",
        index=False,
    )

    print()
    print("Dataset generated successfully.")
    print(f"Orders:        {len(orders)}")
    print(f"Payments:      {len(payments)}")
    print(f"Settlements:   {len(settlements)}")
    print(f"Ground truth:  {len(ground_truth)}")

    print()
    print("Exception distribution:")
    print(
        ground_truth[
            "exception_type"
        ].value_counts()
    )


if __name__ == "__main__":
    main()