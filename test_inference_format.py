"""Mock inference test to verify OpenEnv output format without actual LLM calls."""
import os
import sys
import json

# Set up environment variables
os.environ['HF_TOKEN'] = 'test-mock-token'
os.environ['API_BASE_URL'] = 'https://router.huggingface.co/v1'
os.environ['MODEL_NAME'] = 'meta-llama/Llama-2-7b-chat'
os.environ['ENV_BASE_URL'] = 'http://127.0.0.1:7860'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'receipt-reconciliation'))

import requests

# ── Utility functions from inference.py ──────────────────────────────────────

BENCHMARK = "receipt-reconciliation"
MAX_STEPS = 5
SUCCESS_THRESHOLD = 0.4

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    action_clean = action.replace("\n", " ").replace("\r", "")[:120]
    print(f"[STEP] step={step} action={action_clean} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: list) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

def env_reset(task_id: str) -> dict:
    r = requests.post(f"{os.getenv('ENV_BASE_URL')}/reset", json={"task_id": task_id}, timeout=30)
    r.raise_for_status()
    return r.json()

def env_step(action: dict) -> dict:
    r = requests.post(f"{os.getenv('ENV_BASE_URL')}/step", json=action, timeout=30)
    r.raise_for_status()
    return r.json()

# ── Mock agent logic ──────────────────────────────────────────────────────────

def run_mock_task(task_id: str) -> dict:
    """Run a mock task with predefined actions (no LLM calls)."""
    log_start(task=task_id, env=BENCHMARK, model='mock-test')
    
    rewards = []
    steps_taken = 0
    done = False
    final_score = 0.0
    
    try:
        obs = env_reset(task_id)
        print(f"[DEBUG] Reset: {len(obs['expense_report'])} items, {len(obs['receipts'])} receipts", flush=True)
    except Exception as e:
        log_step(1, "reset_failed", 0.0, True, str(e))
        log_end(success=False, steps=0, score=0.01, rewards=[0.0])
        return {"success": False, "score": 0.01}
    
    # Predefined actions for this mock test
    mock_actions = [
        {
            'action_type': 'flag_discrepancy',
            'item_id': obs['expense_report'][0]['item_id'] if obs['expense_report'] else 'E001',
            'finding_type': 'amount_mismatch',
            'description': 'Mock: Testing amount flag',
            'severity': 'medium',
            'confidence': 0.75
        },
        {
            'action_type': 'approve_item' if len(obs['expense_report']) > 1 else 'request_info',
            'item_id': obs['expense_report'][1]['item_id'] if len(obs['expense_report']) > 1 else 'E001',
            'description': 'Mock: Requesting clarification',
            'confidence': 0.6
        },
        {
            'action_type': 'submit_report',
            'description': 'Mock: Submitting audit findings',
            'confidence': 0.8
        }
    ]
    
    try:
        for step, action_dict in enumerate(mock_actions, 1):
            if done or step > MAX_STEPS:
                break
            
            try:
                result = env_step(action_dict)
                obs = result["observation"]
                reward = float(result["reward"]["value"])
                done = result["done"]
                error_msg = None
            except Exception as e:
                reward = 0.0
                done = True
                error_msg = str(e)
            
            rewards.append(reward)
            steps_taken = step
            
            action_label = f"{action_dict.get('action_type', '?')}({action_dict.get('item_id', '')[:10]})"
            log_step(step=step, action=action_label, reward=reward, done=done, error=error_msg)
            
            if done:
                breakdown = result.get("reward", {}).get("breakdown", {})
                final_score = breakdown.get("score", reward)
                break
    
    finally:
        if not rewards:
            rewards = [0.0]
        
        norm_score = final_score if final_score > 0.0 else (sum(rewards) / len(rewards))
        norm_score = max(0.01, min(norm_score, 0.99))
        success = norm_score >= SUCCESS_THRESHOLD
        
        log_end(success=success, steps=steps_taken, score=norm_score, rewards=rewards)
        return {"success": success, "score": norm_score, "steps": steps_taken}

# ── Main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("[DEBUG] Running mock inference test for OpenEnv format validation...", flush=True)
    result = run_mock_task('task_easy')
    print(f"[DEBUG] Mock result: {result}", flush=True)
