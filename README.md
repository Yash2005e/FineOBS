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

<!-- <p align="center">
  🔴 <a href="YOUR_LIVE_DEMO_URL"><b>Live Demo</b></a>
  &nbsp;&nbsp;•&nbsp;&nbsp;
  🎥 <a href="YOUR_VIDEO_URL"><b>5-Minute Demo</b></a>
  &nbsp;&nbsp;•&nbsp;&nbsp;
  📦 <a href="YOUR_RELEASE_URL"><b>v1.0.0 Release</b></a>
</p> -->



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



🧯 What Broke & How i Got Out

The most important failure was not a package installation problem. It was the limitation of the original reconciliation strategy.

The first approach relied too heavily on exact transaction identifiers. It performed well on clean data but became unreliable when references were missing, altered or ambiguous.



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
