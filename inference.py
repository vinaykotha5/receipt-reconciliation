"""
inference.py — Baseline agent for Receipt Reconciliation Investigator (OpenEnv)

Required environment variables:
  HF_TOKEN       Hugging Face API token (mandatory, no default)
  API_BASE_URL   LLM endpoint (default: https://router.huggingface.co/v1)
  MODEL_NAME     Model identifier (default: Qwen/Qwen2.5-72B-Instruct)
  ENV_BASE_URL   Receipt Reconciliation env URL (default: http://localhost:7860)

STDOUT format (strict OpenEnv spec):
  [START] task=<task_name> env=<benchmark> model=<model_name>
  [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
  [END]   success=<true|false> steps=<n> rewards=<r1,r2,...,rn>
"""

import os
import sys
import json
import time
import textwrap
from typing import List, Optional

# Add receipt-reconciliation to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'receipt-reconciliation'))

import requests
from openai import OpenAI

# ── Environment variables ──────────────────────────────────────────────────────

# HF_TOKEN is mandatory — raise immediately if missing
HF_TOKEN = os.getenv("HF_TOKEN")
if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# API_BASE_URL and MODEL_NAME must have defaults
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")

BENCHMARK         = "receipt-reconciliation"
TASKS             = ["task_easy", "task_medium", "task_hard"]
MAX_STEPS         = 18
TEMPERATURE       = 0.2
MAX_TOKENS        = 400
SUCCESS_THRESHOLD = 0.4   # score >= 0.4 counts as success

# OpenAI client — uses HF_TOKEN as the API key
client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)


# ── Stdout loggers — exact OpenEnv spec format ────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val  = str(done).lower()
    # No newlines inside the action string; truncate to keep line readable
    action_clean = action.replace("\n", " ").replace("\r", "")[:120]
    print(
        f"[STEP] step={step} action={action_clean} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}",
        flush=True,
    )


# ── Environment HTTP helpers ───────────────────────────────────────────────────

def env_reset(task_id: str) -> dict:
    r = requests.post(
        f"{ENV_BASE_URL}/reset",
        json={"task_id": task_id},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def env_step(action: dict) -> dict:
    r = requests.post(
        f"{ENV_BASE_URL}/step",
        json=action,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


# ── Prompts ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""
    You are a forensic accountant AI specialising in expense report auditing and fraud detection.

    You will receive an expense report alongside receipts and company expense policy.
    Investigate every line item and identify discrepancies, policy violations, and fraud patterns.

    Respond ONLY with a JSON object — no markdown, no prose, no code fences:
    {
      "action_type": "flag_discrepancy" | "approve_item" | "request_info" | "submit_report",
      "item_id": "<expense item id, or null>",
      "finding_type": "amount_mismatch" | "date_mismatch" | "vendor_mismatch" | "missing_receipt"
                    | "duplicate" | "policy_violation" | "suspicious_pattern" | "approved" | null,
      "description": "<concise explanation>",
      "severity": "low" | "medium" | "high" | "critical" | null,
      "confidence": <float 0.0-1.0>
    }

    Things to check on every item:
    - Claimed amount vs receipt amount (inflation?)
    - Same receipt_id on multiple expense items (duplicate claim?)
    - Vendor name on claim vs vendor name on receipt (mismatch?)
    - No receipt_id and amount > $25 (missing receipt?)
    - Alcohol listed on meal receipts (no alcohol reimbursement policy)
    - Per-person meal cost > $75 (total / attendee count)
    - Hotel rate > $250/night
    - Same vendor + same amount on adjacent dates (shifted-date duplicate?)
    - Same vendor + same day with combined total > $500 (split transaction to dodge approval limit?)
    - Expense date more than 90 days before today (stale claim)

    Strategy:
    1. Read the full expense report and all receipts carefully on step 1.
    2. Use flag_discrepancy for each suspicious item.
    3. Use approve_item for clearly clean items.
    4. Call submit_report once all items have been reviewed.
""").strip()


def build_user_prompt(obs: dict, step: int, history: List[str]) -> str:
    lines = [f"Step {step}/{obs['max_steps']}"]

    if obs.get("message"):
        lines.append(f"Environment says: {obs['message']}")

    # Show full data on step 1; show only findings and history on subsequent steps
    if step == 1:
        lines.append("\n=== EXPENSE REPORT ===")
        for item in obs["expense_report"]:
            lines.append(
                f"  {item['item_id']}: {item['date']} | {item['vendor']} | "
                f"${item['amount']:.2f} | {item['category']} | "
                f"\"{item['description']}\" | receipt_id={item.get('receipt_id') or 'NONE'}"
            )

        lines.append("\n=== RECEIPTS ===")
        for r in obs["receipts"]:
            lines.append(
                f"  {r['receipt_id']}: {r['date']} | {r['vendor']} | "
                f"${r['amount']:.2f} | items={r['items']} | tip=${r.get('tip', 0):.2f}"
            )

        p = obs["policy"]
        lines.append(
            f"\n=== EXPENSE POLICY ===\n"
            f"  Meal limit/person: ${p['meal_limit_per_person']} | "
            f"Hotel/night: ${p['hotel_limit_per_night']} | "
            f"Receipt required above: ${p['requires_receipt_above']} | "
            f"Max claim age: {p['max_advance_days']} days | "
            f"No alcohol: {p['no_alcohol_reimbursement']} | "
            f"Single approval limit: ${p['single_approval_limit']}"
        )

    if obs.get("previous_findings"):
        lines.append(f"\n=== FINDINGS SO FAR ({len(obs['previous_findings'])}) ===")
        for f in obs["previous_findings"][-6:]:
            lines.append(
                f"  {f['item_id']} | {f['finding_type']} | "
                f"{f['severity']} | {f['description'][:80]}"
            )

    if history:
        lines.append("\n=== RECENT ACTIONS ===")
        for h in history[-3:]:
            lines.append(f"  {h}")

    lines.append("\nRespond with a single JSON action object.")
    return "\n".join(lines)


# ── LLM call ──────────────────────────────────────────────────────────────────

def get_model_action(messages: list) -> str:
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        return (completion.choices[0].message.content or "").strip()
    except Exception as exc:
        print(f"[DEBUG] LLM call failed: {exc}", flush=True)
        return json.dumps({
            "action_type": "submit_report",
            "description": f"LLM error fallback: {exc}",
            "confidence": 0.5,
        })


# ── Single task episode ────────────────────────────────────────────────────────

def run_task(task_id: str) -> dict:
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

    rewards:    List[float] = []
    history:    List[str]   = []
    steps_taken = 0
    done        = False
    final_score = 0.0
    result      = {}

    # Always emit [END] even on hard failure
    try:
        obs = env_reset(task_id)
    except Exception as e:
        log_step(1, "reset_failed", 0.0, True, str(e))
        log_end(success=False, steps=0, rewards=[0.0])
        return {"task_id": task_id, "score": 0.001, "steps": 0, "success": False}

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    try:
        for step in range(1, MAX_STEPS + 1):
            if done:
                break

            # Build prompt and call LLM
            user_msg = build_user_prompt(obs, step, history)
            messages.append({"role": "user", "content": user_msg})
            raw = get_model_action(messages)
            messages.append({"role": "assistant", "content": raw})

            # Parse JSON action
            try:
                clean       = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                action_dict = json.loads(clean)
            except json.JSONDecodeError:
                action_dict = {
                    "action_type": "submit_report",
                    "description": "JSON parse error — submitting",
                    "confidence":  0.5,
                }

            # Step the environment
            error_msg = None
            try:
                result = env_step(action_dict)
                obs    = result["observation"]
                reward = float(result["reward"]["value"])
                done   = result["done"]
            except Exception as e:
                reward    = 0.0
                done      = True
                error_msg = str(e)

            rewards.append(reward)
            steps_taken = step

            # Build a compact action label for the [STEP] line
            action_label = (
                f"{action_dict.get('action_type', '?')}("
                f"{action_dict.get('item_id', '') or ''}"
                f"{':' + action_dict.get('finding_type', '') if action_dict.get('finding_type') else ''})"
            )
            log_step(step=step, action=action_label, reward=reward, done=done, error=error_msg)

            history.append(f"step={step} {action_label} reward={reward:.2f}")

            # Capture the grader's final score when the episode ends
            if done and result:
                breakdown   = result.get("reward", {}).get("breakdown", {})
                final_score = breakdown.get("score", reward)

            if done:
                break

            time.sleep(0.25)

    finally:
        if not rewards:
            rewards = [0.0]

        # Normalise to [0, 1]: use grader score if available, else mean step reward
        norm_score = final_score if final_score > 0.0 else (sum(rewards) / len(rewards))
        norm_score = min(max(norm_score, 0.001), 0.999)
        success    = norm_score >= SUCCESS_THRESHOLD

        # [END] format: success= steps= rewards=  (no score= field per spec)
        log_end(success=success, steps=steps_taken, rewards=rewards)

    return {
        "task_id": task_id,
        "score":   norm_score,
        "steps":   steps_taken,
        "success": success,
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    results = []
    for task_id in TASKS:
        r = run_task(task_id)
        results.append(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
