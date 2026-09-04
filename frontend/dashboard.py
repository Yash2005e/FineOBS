from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
import requests
import streamlit as st


# ==========================================================
# CONFIGURATION
# ==========================================================

API_BASE_URL = os.getenv(
    "FINEOBS_API_URL",
    "http://localhost:8000",
)


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="FineOBS | Finance Controller",
    page_icon="💰",
    layout="wide",
)


# ==========================================================
# CUSTOM STYLING
# ==========================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.5rem;
    }

    .fineobs-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0;
    }

    .fineobs-subtitle {
        color: #777;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #777;
    }

    .exception-card {
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        margin-bottom: 0.75rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# API HELPERS
# ==========================================================

def api_get(
    endpoint: str,
    params: dict | None = None,
):
    response = requests.get(
        f"{API_BASE_URL}{endpoint}",
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def api_post(
    endpoint: str,
    payload: dict,
):
    response = requests.post(
        f"{API_BASE_URL}{endpoint}",
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    '<div class="fineobs-title">FineOBS</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="fineobs-subtitle">
    AI Finance Controller · Reconciliation & Exception Operations
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.header("Batch Control")

    batch_name = st.text_input(
        "Batch name",
        value="fineobs_demo_batch",
    )

    run_batch = st.button(
        "Run Reconciliation",
        use_container_width=True,
        type="primary",
    )

    st.divider()

    st.caption(
        f"API: {API_BASE_URL}"
    )

    if st.button(
        "Refresh Dashboard",
        use_container_width=True,
    ):
        st.rerun()


# ==========================================================
# RUN BATCH
# ==========================================================

if run_batch:

    with st.spinner(
        "Running FineOBS reconciliation..."
    ):

        try:

            batch_result = api_post(
                "/reconcile/smart",
                {
                    "batch_name": batch_name
                },
            )

            st.session_state[
                "latest_batch"
            ] = batch_result

            st.success(
                "Reconciliation completed successfully."
            )

        except requests.RequestException as error:

            st.error(
                f"FineOBS API error: {error}"
            )

        except Exception as error:

            st.error(
                f"Unexpected error: {error}"
            )


# ==========================================================
# LOAD SUMMARY
# ==========================================================

try:

    summary = api_get(
        "/summary"
    )

except Exception:

    summary = {
        "total_exceptions": 0,
        "open": 0,
        "approved": 0,
        "rejected": 0,
        "overridden": 0,
    }


# ==========================================================
# LATEST BATCH
# ==========================================================

latest_batch = st.session_state.get(
    "latest_batch"
)


# ==========================================================
# KPI SECTION
# ==========================================================

st.subheader(
    "Controller Overview"
)

if latest_batch:

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Records",
            latest_batch[
                "total_records"
            ],
        )

    with col2:
        st.metric(
            "Match Rate",
            f"{latest_batch['match_rate']:.2f}%",
        )

    with col3:
        st.metric(
            "Precision",
            f"{latest_batch['precision']:.2f}%",
        )

    with col4:
        st.metric(
            "Recall",
            f"{latest_batch['recall']:.2f}%",
        )

    with col5:
        st.metric(
            "F1 Score",
            f"{latest_batch['f1_score']:.2f}%",
        )

    st.caption(
        f"Batch: {latest_batch['batch_id']}"
    )

else:

    st.info(
        "Run a reconciliation batch to populate the controller metrics."
    )


# ==========================================================
# OPERATIONAL METRICS
# ==========================================================

if latest_batch:

    st.subheader(
        "Operational Metrics"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Matched",
            latest_batch[
                "matched_records"
            ],
        )

    with col2:
        st.metric(
            "Review",
            latest_batch[
                "review_records"
            ],
        )

    with col3:
        st.metric(
            "Unresolved",
            latest_batch[
                "unresolved_records"
            ],
        )

    with col4:
        st.metric(
            "Throughput",
            f"{latest_batch['throughput_records_per_second']:.2f}/sec",
        )


# ==========================================================
# DECISION SOURCES
# ==========================================================

if latest_batch:

    st.subheader(
        "Decision Sources"
    )

    decision_sources = latest_batch.get(
        "decision_source",
        {},
    )

    if decision_sources:

        source_df = pd.DataFrame(
            {
                "Decision Source": list(
                    decision_sources.keys()
                ),
                "Records": list(
                    decision_sources.values()
                ),
            }
        )

        st.bar_chart(
            source_df.set_index(
                "Decision Source"
            )
        )

    else:

        st.info(
            "No decision-source data available."
        )


# ==========================================================
# EXCEPTION DISTRIBUTION
# ==========================================================

if latest_batch:

    st.subheader(
        "Exception Distribution"
    )

    exception_distribution = latest_batch.get(
        "exception_distribution",
        {},
    )

    if exception_distribution:

        exception_df = pd.DataFrame(
            {
                "Exception Type": list(
                    exception_distribution.keys()
                ),
                "Records": list(
                    exception_distribution.values()
                ),
            }
        )

        st.bar_chart(
            exception_df.set_index(
                "Exception Type"
            )
        )

    else:

        st.info(
            "No exceptions detected in this batch."
        )


# ==========================================================
# EXCEPTION QUEUE
# ==========================================================

st.subheader(
    "Exception Queue"
)

try:

    exceptions = api_get(
        "/exceptions",
        params={
            "status": "OPEN"
        },
    )

except Exception:

    exceptions = []


if not exceptions:

    st.success(
        "No open exceptions."
    )

else:

    st.write(
        f"{len(exceptions)} open exception(s)"
    )

    for exception in exceptions[:25]:

        exception_id = exception[
            "id"
        ]

        payment_id = exception[
            "payment_id"
        ]

        exception_type = exception[
            "exception_type"
        ]

        confidence = exception.get(
            "confidence"
        )

        with st.expander(
            f"#{exception_id} · "
            f"{exception_type} · "
            f"{payment_id}"
        ):

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(
                    "**Payment ID**"
                )
                st.write(
                    payment_id
                )

                st.write(
                    "**Order ID**"
                )
                st.write(
                    exception.get(
                        "order_id"
                    )
                )

            with col2:

                st.write(
                    "**Exception**"
                )
                st.write(
                    exception_type
                )

                st.write(
                    "**Difference**"
                )
                st.write(
                    exception.get(
                        "difference_amount"
                    )
                )

            with col3:

                st.write(
                    "**Confidence**"
                )

                if confidence is not None:
                    st.write(
                        f"{confidence:.2%}"
                    )
                else:
                    st.write(
                        "N/A"
                    )

                st.write(
                    "**Status**"
                )

                st.write(
                    exception[
                        "status"
                    ]
                )

            st.write(
                "**Explanation**"
            )

            st.write(
                exception.get(
                    "explanation",
                    "No explanation available.",
                )
            )

            st.divider()

            reviewer = st.text_input(
                "Reviewer",
                value="finance_reviewer",
                key=f"reviewer_{exception_id}",
            )

            comment = st.text_area(
                "Comment",
                value="",
                key=f"comment_{exception_id}",
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                if st.button(
                    "Approve",
                    key=f"approve_{exception_id}",
                ):

                    try:

                        api_post(
                            f"/exceptions/{exception_id}/approve",
                            {
                                "reviewer": reviewer,
                                "comment": comment,
                            },
                        )

                        st.success(
                            "Exception approved."
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Approval failed: {error}"
                        )

            with c2:

                if st.button(
                    "Reject",
                    key=f"reject_{exception_id}",
                ):

                    try:

                        api_post(
                            f"/exceptions/{exception_id}/reject",
                            {
                                "reviewer": reviewer,
                                "comment": comment,
                            },
                        )

                        st.success(
                            "Exception rejected."
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Rejection failed: {error}"
                        )

            with c3:

                if st.button(
                    "Override",
                    key=f"override_{exception_id}",
                ):

                    try:

                        api_post(
                            f"/exceptions/{exception_id}/override",
                            {
                                "reviewer": reviewer,
                                "comment": comment,
                            },
                        )

                        st.success(
                            "Exception overridden."
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Override failed: {error}"
                        )


# ==========================================================
# AUDIT TRAIL
# ==========================================================

st.subheader(
    "Audit Trail"
)

try:

    audit_logs = api_get(
        "/audit"
    )

except Exception:

    audit_logs = []


if audit_logs:

    audit_rows = []

    for log in audit_logs[:50]:

        audit_rows.append(
            {
                "Time": log.get(
                    "created_at"
                ),
                "Entity": log.get(
                    "entity_type"
                ),
                "ID": log.get(
                    "entity_id"
                ),
                "Action": log.get(
                    "action"
                ),
                "Old Status": log.get(
                    "old_status"
                ),
                "New Status": log.get(
                    "new_status"
                ),
                "Actor": log.get(
                    "actor"
                ),
                "Comment": log.get(
                    "comment"
                ),
            }
        )

    audit_df = pd.DataFrame(
        audit_rows
    )

    st.dataframe(
        audit_df,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No audit events yet."
    )


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "FineOBS · AI Finance Controller · "
    f"Dashboard refreshed {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)