"""Quick smoke test for all OpenEnv compliance fixes."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'receipt-reconciliation'))

from environment.env import ReceiptReconciliationEnv
from environment.models import Action, ActionType, FindingType, Severity, Observation

print("1. Imports OK")

# Test reset
e = ReceiptReconciliationEnv()
obs = e.reset('task_easy')
print(f"2. Reset OK: policy type={type(obs.policy).__name__}")

# Test serialization
d = obs.model_dump()
print(f"3. Serialization OK: {len(d['expense_report'])} items")

# Test flag step
a = Action(
    action_type=ActionType.FLAG_DISCREPANCY,
    item_id='E001',
    finding_type=FindingType.AMOUNT_MISMATCH,
    description='Amount mismatch test',
    severity=Severity.HIGH,
    confidence=0.9
)
obs2, r, done, info = e.step(a)
print(f"4. Flag step OK: reward={r.value}")

# Test submit with bonus
a2 = Action(action_type=ActionType.SUBMIT_REPORT, description='final report')
obs3, r2, done2, info2 = e.step(a2)
submit_bonus = r2.breakdown.get("submit_bonus", "MISSING")
print(f"5. Submit OK: score={r2.value}, submit_bonus={submit_bonus}")
assert submit_bonus == 0.05, f"Expected submit_bonus=0.05, got {submit_bonus}"

# Test all 3 tasks run cleanly
for task_id in ["task_easy", "task_medium", "task_hard"]:
    e2 = ReceiptReconciliationEnv()
    obs_t = e2.reset(task_id)
    n_items = len(obs_t.expense_report)
    n_receipts = len(obs_t.receipts)
    # Submit immediately to get a score
    a_sub = Action(action_type=ActionType.SUBMIT_REPORT, description='auto-submit')
    _, r_sub, _, _ = e2.step(a_sub)
    assert 0.0 <= r_sub.value <= 1.0, f"Score out of range: {r_sub.value}"
    print(f"6. {task_id}: {n_items} items, {n_receipts} receipts, score={r_sub.value}")

# Test log format
from inference import log_start, log_step, log_end
print("\n--- Output format demo ---")
log_start(task="task_easy", env="receipt-reconciliation", model="test-model")
log_step(step=1, action="flag_discrepancy(E001:amount_mismatch)", reward=0.09, done=False, error=None)
log_step(step=2, action="submit_report()", reward=0.69, done=True, error=None)
log_end(success=True, steps=2, score=0.69, rewards=[0.09, 0.69])
print("--- End demo ---")

print("\nALL TESTS PASSED")
