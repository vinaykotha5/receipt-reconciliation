"""Quick test to verify environment step execution and rewards."""
import requests
import json

# Reset task_easy
r1 = requests.post('http://127.0.0.1:7860/reset', json={'task_id': 'task_easy'})
obs = r1.json()
print("=== RESET task_easy ===")
print(f"Expense items: {len(obs['expense_report'])}")
print(f"Receipts: {len(obs['receipts'])}")
first_item = obs['expense_report'][0]
print(f"First item: {first_item['item_id']} | {first_item['vendor']} | ${first_item['amount']:.2f}")

# Take a step: flag first item
action = {
    'action_type': 'flag_discrepancy',
    'item_id': first_item['item_id'],
    'finding_type': 'amount_mismatch',
    'description': 'Testing amount discrepancy',
    'severity': 'medium',
    'confidence': 0.7
}
r2 = requests.post('http://127.0.0.1:7860/step', json=action)
result = r2.json()
print("\n=== STEP 1 Result ===")
print(f"Reward value: {result['reward']['value']:.2f}")
print(f"Reward breakdown: {result['reward'].get('breakdown', 'N/A')}")
print(f"Done: {result['done']}")
print(f"Info: {result['info']}")

# Take another step: submit report
action2 = {
    'action_type': 'submit_report',
    'description': 'Submitting findings',
    'confidence': 0.8
}
r3 = requests.post('http://127.0.0.1:7860/step', json=action2)
result2 = r3.json()
print("\n=== STEP 2 (Submit Report) ===")
print(f"Reward value: {result2['reward']['value']:.2f}")
print(f"Reward breakdown: {result2['reward'].get('breakdown', 'N/A')}")
print(f"Done: {result2['done']}")
print(f"Info: {result2['info']}")
print("\n✅ API endpoint test complete")
