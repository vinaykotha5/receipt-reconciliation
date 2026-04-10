---
title: Receipt Reconciliation Investigator
emoji: 🧾
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
  - finance
  - receipt
  - reconciliation
  - fraud-detection
  - agent-environment
---
# Receipt Reconciliation Investigator

**An OpenEnv environment for AI agent expense fraud detection and receipt reconciliation.**

---

## Overview

Finance teams process thousands of expense reports every month. Detecting mismatches — inflated amounts, duplicate submissions, missing receipts, policy violations, and subtle fraud patterns like split transactions — is time-consuming and error-prone when done manually.

This environment puts an AI agent in the role of a forensic accountant. Given an expense report and the corresponding receipts, the agent must identify every discrepancy, flag suspicious patterns, and produce a structured audit finding report.

This is a real-world task. Companies like Concur, Expensify, and SAP have built entire product lines around it. The environment models the actual decision logic used in accounts-payable review workflows.

---

## Environment description

The agent receives:
- An **expense report** — a list of line items, each with a date, vendor, amount, category, description, and claimed receipt reference
- The actual **receipts** — what was printed at point of sale
- A company **expense policy** — per-person meal limits, hotel caps, receipt thresholds, alcohol rules, claim age limits

The agent must investigate all items and submit a findings report before the step budget runs out.

---

## Action space

| `action_type`      | Description |
|--------------------|-------------|
| `flag_discrepancy` | Flag an issue on a specific expense item. Requires `item_id`, `finding_type`, `severity`, `description`, `confidence`. |
| `approve_item`     | Mark an item as clean and reimbursable. |
| `request_info`     | Request additional information (uses a step, no state change). |
| `submit_report`    | Finalise the audit. Triggers grading and ends the episode. |

**Finding types:** `amount_mismatch`, `date_mismatch`, `vendor_mismatch`, `missing_receipt`, `duplicate`, `policy_violation`, `suspicious_pattern`, `approved`

**Severity levels:** `low`, `medium`, `high`, `critical`

---

## Observation space

```json
{
  "task_id": "task_easy",
  "expense_report": [ { "item_id": "E001", "date": "...", "vendor": "...", "amount": 0.0, ... } ],
  "receipts":       [ { "receipt_id": "R001", "date": "...", "vendor": "...", "amount": 0.0, "items": [] } ],
  "policy": {
    "meal_limit_per_person": 75.0,
    "hotel_limit_per_night": 250.0,
    "requires_receipt_above": 25.0,
    "max_advance_days": 90,
    "no_alcohol_reimbursement": true,
    "single_approval_limit": 500.0
  },
  "step_number": 1,
  "max_steps": 20,
  "previous_findings": [],
  "message": "..."
}
```

---

## Tasks

### Task 1 — Easy: Single Receipt Match
- 1 expense item, 1 receipt
- One clear amount mismatch ($124.50 claimed vs $98.50 on receipt)
- Expected score for a capable agent: **0.75–0.90**

### Task 2 — Medium: Multi-Receipt Expense Report
- 5 expense items, 3 receipts
- Issues: duplicate receipt reference, alcohol in meal receipt, vendor name mismatch, hotel over policy limit
- Expected score: **0.50–0.70**

### Task 3 — Hard: Fraud Detection Audit
- 10 expense items, 9 receipts
- Subtle fraud: split transaction to evade $500 approval threshold, personal dinner disguised as team meal (attendee count mismatch), inflated hotel amount, shifted-date duplicate Lyft claim, missing receipt above threshold, stale claim outside 90-day window, alcohol in client dinner
- Expected score for frontier models: **0.25–0.50**

---

## Reward function

Rewards are dense — the agent receives signal throughout the episode, not just at the end.

| Signal | Value |
|--------|-------|
| Correct required finding (partial, mid-episode) | `+0.10 × confidence` |
| Correct optional finding | `+0.05 × confidence` |
| False positive (flagging a clean item) | `−0.05` |
| Correctly approving a clean item | `+0.05` |
| Approving a flagged item | `−0.05` |
| Final score on submit | Replaces cumulative (see below) |

**Final scoring weights (on `submit_report`):**

| Component | Weight |
|-----------|--------|
| Required finding recall | 55% |
| Optional finding bonus | 15% |
| False positive penalty | −20% |
| Confidence calibration | 10% |
| Submit bonus | 5% |

Timeout (no submit within 20 steps) applies an 85% cap on the final score.

---

## Setup

### Local development

```bash
git clone <repo>
cd receipt-reconciliation
pip install -r requirements.txt

# Start the environment server
uvicorn api.main:app --host 0.0.0.0 --port 7860 --reload

# In another terminal, run the baseline agent
export OPENAI_API_KEY=sk-...
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o-mini
export ENV_BASE_URL=http://localhost:7860
python inference.py
```

### Docker

```bash
docker build -t receipt-recon .
docker run -p 7860:7860 \
  -e OPENAI_API_KEY=sk-... \
  receipt-recon
```

### API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/health` | Health check |
| `GET`  | `/tasks` | List available tasks |
| `POST` | `/reset` | Start episode (`{"task_id": "task_easy"}`) |
| `POST` | `/step` | Take action (see action schema above) |
| `GET`  | `/state` | Full environment state |

---

## Baseline scores

Measured with `gpt-4o-mini` (temperature 0.2):

| Task | Score | Notes |
|------|-------|-------|
| task_easy | 0.72 | Finds the amount mismatch reliably |
| task_medium | 0.55 | Catches duplicate + alcohol; misses vendor name mismatch |
| task_hard | 0.33 | Finds inflated hotel and missing receipt; rarely detects split-transaction fraud |
| **Average** | **0.53** | |

> **Score ceiling:** The grader is designed so even a perfect agent scores ~0.85 (not 1.0).
> This reflects real-world auditing uncertainty — the 0.10 confidence calibration component
> rewards well-calibrated agents over overconfident ones. A score of 0.70+ is excellent.

---

## Environment variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | API key for LLM calls |
| `API_BASE_URL` | LLM endpoint base URL |
| `MODEL_NAME` | Model identifier |
| `ENV_BASE_URL` | URL of the running environment (default: `http://localhost:7860`) |
| `HF_TOKEN` | Hugging Face token (for HF Spaces deployment) |

---

## Project structure

```
receipt-reconciliation/
├── inference.py          # Baseline agent (OpenAI client, structured logging)
├── openenv.yaml          # OpenEnv metadata
├── Dockerfile            # Container definition
├── requirements.txt
├── README.md
├── app.py                # HF Spaces entrypoint
├── environment/
│   ├── __init__.py
│   ├── env.py            # Core environment (step/reset/state)
│   ├── models.py         # Pydantic typed models
│   └── tasks.py          # Task seed data + deterministic graders
└── api/
    ├── __init__.py
    └── main.py           # FastAPI HTTP wrapper
```
