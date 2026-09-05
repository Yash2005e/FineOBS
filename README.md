<p align="center">
  <img src="https://img.shields.io/badge/RAZORPAY%20BUILDAThON-AI%20FINANCE%20CONTROLLER-C98A1A?style=for-the-badge" alt="Razorpay Buildathon">
  <img src="https://img.shields.io/badge/FineOBS-v1.0.0-111111?style=for-the-badge" alt="FineOBS Version">
  <img src="https://img.shields.io/badge/status-working-success?style=for-the-badge" alt="Status">
</p>

<p align="center">
  <b>Automate what can be trusted. Expose what cannot.</b>
</p>

<p align="center">
  AI-assisted financial reconciliation, exception management and auditability for payment, order and settlement operations.
</p>

<p align="center">
  🔴 <a href="YOUR_LIVE_DEMO_URL"><b>Live Demo</b></a>
  &nbsp;&nbsp;•&nbsp;&nbsp;
  🎥 <a href="YOUR_VIDEO_URL"><b>5-Minute Demo</b></a>
  &nbsp;&nbsp;•&nbsp;&nbsp;
  📦 <a href="YOUR_RELEASE_URL"><b>v1.0.0 Release</b></a>
</p>

🧭 Table of Contents

What is FineOBS?

The Problem

The Idea

How FineOBS Works

Why This Approach

Key Features

Dashboard

Benchmark

Architecture

Tech Stack

Project Structure

Run Locally

API

Evaluation

What Broke & How We Got Out

Design Principles

Roadmap

Buildathon

Author

🎯 What is FineOBS?

FineOBS is an AI-assisted finance controller that closes a reconciliation loop across orders, payments and settlements.

It is designed for the messy part of finance operations:

Multiple financial sources
          ↓
   Records don't align
          ↓
 Exact matching is insufficient
          ↓
 Candidate matching + verification
          ↓
   Safe financial decision
          ↓
 Exception / human review
          ↓
       Audit trail
          ↓
    Measured outcome

FineOBS is intentionally conservative.

A financially uncertain record should become a visible exception, not a confidently wrong match.

💡 The Problem

Finance operations teams frequently reconcile data from multiple systems.

The records can contain:

missing settlements

duplicate settlements

amount mismatches

settlement delays

noisy transaction references

incomplete identifiers

ambiguous candidates

A simple exact-match system is fast but fragile.

A fully autonomous AI system is flexible but should not be allowed to improvise financial truth.

So FineOBS uses a layered controller:

Deterministic controls
        +
Intelligent matching
        +
Verification
        +
Human review
        +
Auditability

🧠 The Idea

The key question is not:

"Can we match this transaction?"

It is:

"Do we have enough evidence to safely accept this match?"

FineOBS therefore evaluates:

Reference similarity
        +
Amount similarity
        +
Customer similarity
        +
Date similarity
        ↓
Candidate score
        +
Candidate margin
        ↓
Decision

The candidate margin is important.

A candidate with a 0.97 score is not equally trustworthy when the second-best candidate scores 0.40 versus 0.96.

⚙️ How FineOBS Works

01 · Ingest

Load:

Orders
Payments
Settlements

02 · Normalize

Standardize:

dates

amounts

identifiers

references

missing values

03 · Deterministic Reconciliation

Check:

Order exists?
Payment exists?
Exact settlement?
Amount agrees?
Settlement on time?
Duplicate settlement?

04 · Intelligent Matching

When exact matching fails:

Candidate blocking
        ↓
Reference similarity
Amount similarity
Customer similarity
Date similarity
        ↓
Weighted score
        ↓
Confidence + candidate margin

05 · Decision

HIGH CONFIDENCE
       ↓
MATCHED

MODERATE / AMBIGUOUS
       ↓
REVIEW

WEAK / INSUFFICIENT
       ↓
UNRESOLVED

06 · Verification

Review cases can be sent to the verification layer with structured evidence.

07 · Exception Management

Uncertain cases enter an operational review queue.

08 · Audit

Every important action is recorded.

09 · Evaluation

The entire batch is compared against known ground truth.

🧩 Key Features

🔍 Deterministic Reconciliation

Financial control checks for:

Check

Purpose

Order existence

Prevent orphan payment records

Exact settlement lookup

Handle clean records cheaply

Amount validation

Catch monetary discrepancies

Timing validation

Detect settlement delays

Duplicate detection

Prevent double settlement interpretation

Missing settlement detection

Surface unmatched payments

🧠 Intelligent Candidate Matching

FineOBS uses several independent signals:

<p>
  <img src="https://img.shields.io/badge/Reference%20Similarity-MULTI%20SIGNAL-6C2DC7?style=for-the-badge" alt="Reference Similarity">
  <img src="https://img.shields.io/badge/Amount%20Similarity-FINANCIAL-00897B?style=for-the-badge" alt="Amount Similarity">
  <img src="https://img.shields.io/badge/Customer%20Similarity-ENTITY-1565C0?style=for-the-badge" alt="Customer Similarity">
  <img src="https://img.shields.io/badge/Date%20Similarity-TEMPORAL-8E44AD?style=for-the-badge" alt="Date Similarity">
</p>

Rather than comparing every possible record blindly, FineOBS first reduces the candidate pool and then performs detailed scoring.

🤖 AI-Assisted Verification

The verification layer receives structured evidence such as:

Payment details
Candidate settlement
Alternative candidates
Confidence
Candidate margin
Amount difference
Customer match
Date difference

Possible decisions:

AUTO_RECONCILE
HUMAN_REVIEW
UNRESOLVED

A policy gate prevents weak evidence from being treated as a safe autonomous decision.

The current development pipeline includes a conservative local fallback, so the system does not depend on a paid external API just to run the benchmark.

🚨 Exception Operations

Every uncertain case can enter a review workflow:

OPEN
 ↓
APPROVE
REJECT
OVERRIDE

The reviewer can inspect the evidence before changing the state.

🧾 Auditability

The audit layer records:

Entity
Action
Previous status
New status
Actor
Comment
Timestamp

Example:

SYSTEM
  ↓
CREATED
  ↓
OPEN
  ↓
finance_reviewer
  ↓
APPROVED

🖥️ Dashboard

FineOBS Operations Console



The dashboard surfaces:

batch execution

records processed

match rate

precision

recall

F1 score

throughput

decision sources

exception distribution

exception queue

reviewer actions

audit history

🔎 Intelligent Matching View



The matching layer exposes the evidence used to rank settlement candidates rather than hiding the decision behind one opaque number.

🚨 Exception Queue



Finance reviewers can inspect the transaction evidence and take a controlled action.

🧾 Audit Trail



The final state transition is recorded and traceable.

📊 Benchmark

FineOBS uses a 500-record synthetic finance benchmark with known ground truth.

Benchmark scenarios

✓ Clean reconciliations
✓ Missing settlements
✓ Duplicate settlements
✓ Amount mismatches
✓ Settlement delays
✓ Noisy identifiers
✓ Ambiguous candidates

Final benchmark results

Replace the values below with the final frozen benchmark run before submission.

Metric

Result

Total Records

500

Match Rate

83.20%

Precision

82.93%

Recall

96.37%

F1 Score

89.15%

Matched

416

Review

4

Unresolved

30

Throughput

101.89 records/sec

Exception categories

Exception Type

Records

Missing Settlement

XX

Amount Mismatch

XX

Duplicate Settlement

XX

Settlement Delay

XX

Ambiguous Match

XX

Insufficient Evidence

XX

These numbers should be updated from the final reproducible run rather than copied from an earlier development state.

📈 Why These Metrics Matter

FineOBS does not optimize only for the number of records it can force into MATCHED.

It reports:

Match Rate
     +
Precision
     +
Recall
     +
F1
     +
Review Rate
     +
Unresolved Rate
     +
Throughput

The distinction

Match rate asks:

How many records did the system classify as matched?

Precision asks:

How many of those matches were actually correct?

Recall asks:

How many truly matchable records did the system recover?

Unresolved rate asks:

How much uncertainty did the controller refuse to hide?

That distinction is central to financial automation.

🏗️ Architecture

                    ┌───────────────────────┐
                    │ Orders / Payments /   │
                    │ Settlements           │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Data Normalization    │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Deterministic Engine  │
                    └───────────┬───────────┘
                                │
                          Exact match?
                           /         \
                         YES          NO
                          │            │
                          │            ▼
                          │    ┌───────────────┐
                          │    │ Candidate     │
                          │    │ Generation    │
                          │    └───────┬───────┘
                          │            ▼
                          │    ┌───────────────┐
                          │    │ Multi-Signal  │
                          │    │ Scoring       │
                          │    └───────┬───────┘
                          │            ▼
                          │    Confidence + Margin
                          │            │
                          └──────┬─────┘
                                 ▼
                       ┌────────────────────┐
                       │ Decision Layer     │
                       └──────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
                 MATCHED        REVIEW      UNRESOLVED
                                  │
                                  ▼
                       ┌────────────────────┐
                       │ Verification       │
                       │ Layer              │
                       └──────────┬─────────┘
                                  ▼
                       ┌────────────────────┐
                       │ Risk / Policy Gate │
                       └──────────┬─────────┘
                                  ▼
                       ┌────────────────────┐
                       │ Exception Queue    │
                       └──────────┬─────────┘
                                  ▼
                       ┌────────────────────┐
                       │ Audit Trail        │
                       └──────────┬─────────┘
                                  ▼
                       ┌────────────────────┐
                       │ Evaluation Engine  │
                       └────────────────────┘

🛠️ Tech Stack

Backend

<p>
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/SQLite-Development-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
</p>

Data & Matching

<p>
  <img src="https://img.shields.io/badge/Pandas-Data%20Processing-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/RapidFuzz-Fuzzy%20Matching-6C2DC7?style=for-the-badge" alt="RapidFuzz">
</p>

Frontend

<p>
  <img src="https://img.shields.io/badge/Streamlit-Operations%20Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
</p>

AI / Verification

<p>
  <img src="https://img.shields.io/badge/Structured%20Verification-AI%20Ready-7B61FF?style=for-the-badge" alt="AI Verification">
</p>

Development

<p>
  <img src="https://img.shields.io/badge/Git-GitHub-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git">
  <img src="https://img.shields.io/badge/GitHub-Codespaces-24292E?style=for-the-badge&logo=github" alt="Codespaces">
</p>

📁 Project Structure

FineOBS/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── audit.py
│   │   │       ├── exceptions.py
│   │   │       ├── reconcile.py
│   │   │       ├── smart_reconcile.py
│   │   │       └── summary.py
│   │   │
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── agents/
│   │   │   ├── matching/
│   │   │   ├── reconciliation/
│   │   │   └── reporting/
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── data/
│   ├── generated/
│   └── ground_truth/
│
├── docs/
│   ├── screenshots/
│   └── evaluation.md
│
├── frontend/
│   ├── app.py
│   └── dashboard.py
│
├── scripts/
│   ├── generate_data.py
│   ├── run_reconciliation.py
│   ├── run_intelligent_reconciliation.py
│   ├── evaluate_reconciliation.py
│   ├── evaluate_smart_reconciliation.py
│   └── final_pipeline_test.py
│
├── .env.example
├── .gitignore
└── README.md

🚀 Run Locally

Prerequisites

Python 3.11+

Git

Clone

git clone YOUR_GITHUB_REPOSITORY_URL
cd FineOBS

Create virtual environment

Linux / macOS / Codespaces

python -m venv backend/.venv
source backend/.venv/bin/activate

Windows

python -m venv backend\.venv
backend\.venv\Scripts\activate

Install dependencies

pip install -r backend/requirements.txt

▶️ Start the API

uvicorn backend.app.main:app \
  --reload \
  --host 0.0.0.0 \
  --port 8000

API documentation:

http://localhost:8000/docs

Main smart reconciliation endpoint:

POST /reconcile/smart

Example:

{
  "batch_name": "fineobs_demo"
}

🖥️ Start the Dashboard

Open a second terminal:

source backend/.venv/bin/activate

Run:

streamlit run frontend/dashboard.py \
  --server.address 0.0.0.0 \
  --server.port 8501

Open:

http://localhost:8501

🧪 Benchmark Commands

Generate data:

python scripts/generate_data.py

Run deterministic reconciliation:

python -m scripts.run_reconciliation

Run the smart engine:

python -m scripts.test_smart_engine

Evaluate the smart pipeline:

python -m scripts.evaluate_smart_reconciliation

Run the final pipeline smoke test:

python -m scripts.final_pipeline_test

Expected:

============================================================
             PIPELINE TEST PASSED
============================================================

🌐 Public Demo

The public demo is intended to give reviewers a direct way to experience FineOBS without setting up the repository locally.

Live Application

Open FineOBS

Source Code

View on GitHub

Release

FineOBS v1.0.0

Do not expose .env, private keys or local database files in the public repository.

🧾 API Overview

Method

Endpoint

Purpose

GET

/

Service information

GET

/health

Health check

POST

/reconcile

Baseline reconciliation

POST

/reconcile/smart

Smart reconciliation pipeline

GET

/exceptions

Exception queue

GET

/exceptions/{id}

Exception details

POST

/exceptions/{id}/approve

Approve exception

POST

/exceptions/{id}/reject

Reject exception

POST

/exceptions/{id}/override

Override exception

GET

/audit

Audit trail

GET

/summary

Exception summary

📐 Evaluation

FineOBS evaluates the reconciliation system against known ground truth.

Core measures

Precision
Recall
F1 Score
Match Rate
Review Rate
Unresolved Rate
Throughput

Why ground truth?

Because a system that says:

MATCHED: 95%

may still be wrong.

FineOBS therefore separates:

Predicted match
      ↓
Actually correct?
      ↓
Measured performance

This makes the benchmark reproducible and allows different reconciliation strategies to be compared on the same dataset.

🧯 What Broke & How We Got Out

The most important failure was not a package installation problem. It was the limitation of the original reconciliation strategy.

The first approach relied too heavily on exact transaction identifiers. It performed well on clean data but became unreliable when references were missing, altered or ambiguous.

We changed the design to:

Exact matching
      ↓
Candidate generation
      ↓
Multi-signal scoring
      ↓
Confidence + candidate margin
      ↓
Verification / human review

This allowed FineOBS to distinguish between:

Safe automatic reconciliation
        vs
Plausible but ambiguous candidate
        vs
Insufficient evidence

A second challenge was preserving control while increasing automation.

The solution was to introduce:

explicit confidence thresholds

candidate-margin checks

an unresolved state

exception workflows

human approval

audit logs

benchmark evaluation

The resulting principle became:

The controller should know when not to trust a match.

🧠 Design Principles

01 · Deterministic before probabilistic

Use explicit financial controls wherever possible.

02 · Evidence before automation

An automatic decision must have measurable supporting evidence.

03 · Uncertainty is a valid result

UNRESOLVED is preferable to a wrong financial match.

04 · Human-in-the-loop

Ambiguous cases should remain reviewable.

05 · Every important action is auditable

Decision history matters as much as the final state.

06 · Measure the system

Do not judge a reconciliation engine only by how many records it claims to match.

🛣️ Roadmap

✅ Completed

Synthetic 500-record benchmark

Ground-truth dataset

Deterministic reconciliation

Candidate blocking

Fuzzy matching

Confidence scoring

Candidate-margin scoring

Smart reconciliation pipeline

Exception queue

Approve / Reject / Override workflow

Audit trail

Precision / Recall / F1 evaluation

Throughput measurement

Streamlit dashboard

AI verification architecture

🔜 Future

Production payment-provider adapters

PostgreSQL deployment

Role-based access control

Broader AI evaluation

Production observability

Continuous reconciliation monitoring

More advanced anomaly detection

🏆 Razorpay Buildathon

Track

AI Finance Controller

Project

FineOBS

What it solves

FineOBS closes a finance-operations reconciliation loop across payment, order and settlement records while providing:

Automation
    +
Accuracy
    +
Controlled uncertainty
    +
Human review
    +
Auditability
    +
Measured performance

Proof

Working repository

Live application

500-record benchmark

Measured reconciliation metrics

Exception management

Audit trail

5-minute working demo

🎥 5-Minute Demo

The recommended walkthrough:

00:00  Problem + introduction
00:30  FineOBS idea
01:15  Run 500-record batch
02:00  Show metrics
02:30  Open exception
03:00  Approve / reject / override
03:30  Show audit trail
03:45  Explain intelligent matching
04:15  Explain challenge + solution
04:40  Final results + architecture

▶ Watch the 5-Minute FineOBS Demo

👤 Author

Yash Patil

B.Tech Information Technology
SVKM's Global University, Dhule, Maharashtra

<p>
  <img src="https://img.shields.io/badge/AI%2FML-Data%20Driven-7B61FF?style=for-the-badge" alt="AI/ML">
  <img src="https://img.shields.io/badge/FinTech-Reconciliation-C98A1A?style=for-the-badge" alt="FinTech">
  <img src="https://img.shields.io/badge/Buildathon-Razorpay-111111?style=for-the-badge" alt="Razorpay Buildathon">
</p>

<p align="center">
  <b>FineOBS</b><br>
  Automate what can be trusted. Expose what cannot.
</p>
