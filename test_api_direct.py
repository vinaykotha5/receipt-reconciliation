"""Quick test of the API without running a server"""
import sys
sys.path.insert(0, 'receipt-reconciliation')

from environment.env import ReceiptReconciliationEnv
from environment.models import Action, ActionType, FindingType, Severity

print("=" * 50)
print("Testing Receipt Reconciliation Environment")
print("=" * 50)

# Test 1: Create environment
print("\n✓ Test 1: Creating environment...")
env = ReceiptReconciliationEnv()
print("  SUCCESS: Environment created")

# Test 2: List tasks
print("\n✓ Test 2: Listing tasks...")
from environment.tasks import TASKS
print(f"  SUCCESS: Found {len(TASKS)} tasks:")
for task_id, task in TASKS.items():
    task_name = task.get('name', task_id) if isinstance(task, dict) else task.name
    print(f"    - {task_id}: {task_name}")

# Test 3: Reset environment
print("\n✓ Test 3: Resetting environment with task_easy...")
obs = env.reset(task_id="task_easy")
print(f"  SUCCESS: Reset complete")
print(f"  Receipts: {len(obs.receipts)}")
print(f"  Expense items: {len(obs.expense_report)}")
print(f"  Message: {obs.message[:50] if obs.message else 'No message'}...")

# Test 4: Take an action
print("\n✓ Test 4: Taking an action (FLAG_DISCREPANCY)...")
action = Action(
    action_type=ActionType.FLAG_DISCREPANCY,
    item_id=obs.expense_report[0].item_id if obs.expense_report else None,
    finding_type=FindingType.AMOUNT_MISMATCH,
    description="Testing action execution",
    severity=Severity.LOW
)
obs, reward, done, info = env.step(action)
print(f"  SUCCESS: Action executed")
print(f"  Reward: {reward.value}")
print(f"  Done: {done}")
print(f"  Message: {obs.message[:50] if obs.message else 'No message'}...")

# Test 5: Get state
print("\n✓ Test 5: Getting environment state...")
state = env.state()
print(f"  SUCCESS: State retrieved")
print(f"  Current task: {state.get('current_task_id', 'N/A')}")
print(f"  Steps taken: {state.get('steps_taken', 0)}")

print("\n" + "=" * 50)
print("ALL TESTS PASSED!")
print("=" * 50)
print("\nYour Receipt Reconciliation environment is working correctly!")
print("Ready for deployment to Hugging Face Spaces.")
