import requests
import json

url = 'http://127.0.0.1:7860'

print('=== Testing OpenEnv Endpoints ===\n')

# Test 1: Health
print('1. Health (GET)')
try:
    r = requests.get(f'{url}/health', timeout=5)
    print(f'   Status: {r.status_code} ✅')
    print(f'   Response: {r.json()}')
except Exception as e:
    print(f'   Error: {e}')

# Test 2: Tasks
print('\n2. Tasks (GET)')
try:
    r = requests.get(f'{url}/tasks', timeout=5)
    print(f'   Status: {r.status_code} ✅')
    tasks = r.json().get('tasks', [])
    for t in tasks:
        print(f'   - {t["task_id"]} ({t["difficulty"]}): {t["name"]}')
except Exception as e:
    print(f'   Error: {e}')

# Test 3: Reset with proper body
print('\n3. Reset (POST with task_id in body)')
try:
    payload = {'task_id': 'task_easy'}
    r = requests.post(f'{url}/reset', json=payload, timeout=5)
    print(f'   Status: {r.status_code} ✅')
    resp = r.json()
    print(f'   Fields: {list(resp.keys())}')
    print(f'   Items in report: {len(resp.get("expense_report", []))}')
    print(f'   Receipts: {len(resp.get("receipts", []))}')
except Exception as e:
    print(f'   Error: {e}')

# Test 4: Step with action
print('\n4. Step (POST with action)')
try:
    reset_resp = requests.post(f'{url}/reset', json={'task_id': 'task_easy'}, timeout=5)
    obs = reset_resp.json()
    
    action = {
        'action_type': 'flag_discrepancy',
        'item_id': obs['expense_report'][0]['item_id'],
        'finding_type': 'amount_mismatch',
        'description': 'Test flag',
        'severity': 'medium',
        'confidence': 0.8
    }
    r = requests.post(f'{url}/step', json=action, timeout=5)
    print(f'   Status: {r.status_code} ✅')
    result = r.json()
    print(f'   Done: {result["done"]}')
    print(f'   Reward: {result["reward"]["value"]:.2f}')
except Exception as e:
    print(f'   Error: {e}')

print('\n✅ All endpoint tests complete')
