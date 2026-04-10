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

# 🧾 Receipt Reconciliation Investigator

**An OpenEnv environment for AI agent expense fraud detection and receipt reconciliation.**

---

## Overview & Motivation

Finance teams process thousands of expense reports every month. Detecting discrepancies — inflated amounts, duplicate submissions, missing receipts, policy violations, and subtle fraud patterns like split transactions — is time-consuming and error-prone when done manually.

This environment puts an AI agent in the role of a **forensic accountant**. Given an expense report, the corresponding receipts, and a company expense policy, the agent must identify every discrepancy, flag suspicious patterns, and produce a structured audit report.

This is a **real-world task**. Companies like Concur, Expensify, and SAP have built entire product lines around expense reconciliation. The environment models actual decision logic used in accounts-payable review workflows.

---

## Action Space

| `action_type`      | Description |
|--------------------|-------------|
| `flag_discrepancy` | Flag an issue on a specific expense item. Requires `item_id`, `finding_type`, `severity`, `description`, `confidence`. |
| `approve_item`     | Mark an item as clean and reimbursable. |
| `request_info`     | Request additional information (uses a step, no state change). |
| `submit_report`    | Finalise the audit. Triggers final grading and ends the episode. |

**Finding types:** `amount_mismatch`, `date_mismatch`, `vendor_mismatch`, `missing_receipt`, `duplicate`, `policy_violation`, `suspicious_pattern`, `approved`

**Severity levels:** `low`, `medium`, `high`, `critical`

**Confidence:** `float` in `[0.0, 1.0]` — calibration is part of the scoring.

---

## Observation Space

```json
{
  "task_id": "task_easy",
  "expense_report": [
    { "item_id": "E001", "date": "2024-03-15", "vendor": "...", "amount": 124.50, "category": "meals", "description": "...", "receipt_id": "R001" }
  ],
  "receipts": [
    { "receipt_id": "R001", "date": "2024-03-15", "vendor": "...", "amount": 98.50, "items": ["..."], "tax": 8.25, "tip": 0.0 }
  ],
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
- **1** expense item, **1** receipt
- One clear amount mismatch ($124.50 claimed vs $98.50 on receipt)
- Tests basic comparison ability
- **Expected score for a capable agent: 0.75–0.90**

### Task 2 — Medium: Multi-Receipt Expense Report
- **5** expense items, **3** receipts
- Issues: duplicate receipt reference, alcohol in meal receipt, vendor name mismatch, hotel over policy limit
- Tests ability to cross-reference and apply policy rules
- **Expected score: 0.50–0.70**

### Task 3 — Hard: Fraud Detection Audit
- **10** expense items, **9** receipts
- Subtle fraud: split transaction to evade $500 approval threshold, personal dinner disguised as team meal (attendee count mismatch on receipt), inflated hotel amount ($310 claimed / $210 receipt), shifted-date duplicate Lyft claim, missing receipt above threshold, stale claim outside 90-day window, alcohol in client dinner
- Tests deep forensic reasoning and pattern recognition
- **Expected score for frontier models: 0.25–0.50**

---

## Reward Function

Rewards are **dense** — the agent receives signal throughout the episode, not just at the end.

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

Timeout (no submit within 20 steps) → 85% cap on final score.

---

## Baseline Scores

Measured with `Qwen/Qwen2.5-72B-Instruct` (temperature 0.2, via HF Router):

| Task | Score | Notes |
|------|-------|-------|
| task_easy | 0.72 | Finds the amount mismatch reliably |
| task_medium | 0.55 | Catches duplicate + alcohol; misses vendor name mismatch |
| task_hard | 0.33 | Finds inflated hotel and missing receipt; rarely detects split-transaction fraud |
| **Average** | **0.53** | |

> **Scoring design:** Even a perfect agent scores ~0.85 (not 1.0). The 0.10 confidence calibration component rewards well-calibrated agents over overconfident ones. A score above 0.70 is excellent.

---

## Setup & Usage

### Prerequisites

```bash
pip install fastapi uvicorn pydantic openai requests httpx
```

### Start the environment server

```bash
cd receipt-reconciliation
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 7860
```

### Run the baseline agent

```bash
export HF_TOKEN=your_hf_token_here
export ENV_BASE_URL=http://localhost:7860
python inference.py
```

### Docker deployment

```bash
docker build -t receipt-recon .
docker run -p 7860:7860 receipt-recon
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/health` | Health check |
| `GET`  | `/tasks` | List available tasks |
| `POST` | `/reset` | Start episode (`{"task_id": "task_easy"}`) |
| `POST` | `/step` | Take action (see action schema above) |
| `GET`  | `/state` | Full environment state |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HF_TOKEN` | **Yes** | — | Hugging Face API token |
| `API_BASE_URL` | No | `https://router.huggingface.co/v1` | LLM endpoint base URL |
| `MODEL_NAME` | No | `Qwen/Qwen2.5-72B-Instruct` | Model identifier |
| `ENV_BASE_URL` | No | `http://localhost:7860` | URL of the running environment |

---

## Project Structure

```
├── inference.py                    # Baseline agent (root, OpenEnv requirement)
├── openenv.yaml                    # OpenEnv metadata
├── Dockerfile                      # Docker container definition
├── requirements.txt                # Python dependencies
├── app.py                          # HF Spaces entrypoint
├── README.md                       # This file
└── receipt-reconciliation/         # Main environment implementation
    ├── environment/
    │   ├── __init__.py
    │   ├── env.py                  # Core environment (step/reset/state)
    │   ├── models.py               # Pydantic typed models
    │   └── tasks.py                # Task seed data + deterministic graders
    ├── api/
    │   ├── __init__.py
    │   └── main.py                 # FastAPI HTTP wrapper
    ├── openenv.yaml
    ├── requirements.txt
    └── README.md
```

---

## OpenEnv Compliance

- `inference.py` at root directory ✅
- OpenAI Client for all LLM calls ✅
- `HF_TOKEN` mandatory, `API_BASE_URL`/`MODEL_NAME` with defaults ✅
- `[START]`/`[STEP]`/`[END]` stdout format ✅
- Typed Pydantic models for Action, Observation, Reward ✅
- `step()`/`reset()`/`state()` API ✅
- `openenv.yaml` metadata ✅
- 3 tasks with deterministic graders (0.0–1.0) ✅
- Dense reward function with partial progress ✅
- Working Dockerfile ✅
- Tagged with `openenv` ✅
