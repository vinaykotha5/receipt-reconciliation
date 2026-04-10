"""
Preservation Property Tests for OpenEnv Project Structure Fix

**Property 2: Preservation - Runtime Behavior Unchanged**

These tests capture the baseline behavior on UNFIXED code (running from receipt-reconciliation/)
and verify the same behavior after the fix (running from root).

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any

# Add receipt-reconciliation to path for imports
sys.path.insert(0, str(Path(__file__).parent / "receipt-reconciliation"))

from environment.env import ReceiptReconciliationEnv
from environment.models import Action, ActionType, FindingType, Severity


def test_environment_reset_behavior():
    """
    Verify environment reset produces consistent initial observations.
    
    **Preservation Requirement 3.1**: Environment package (env.py, models.py, tasks.py)
    must continue to provide the same Receipt Reconciliation environment functionality.
    """
    env = ReceiptReconciliationEnv()
    
    # Test all three tasks
    for task_id in ["task_easy", "task_medium", "task_hard"]:
        obs = env.reset(task_id=task_id)
        
        # Verify observation structure
        assert obs.task_id == task_id, f"Task ID mismatch for {task_id}"
        assert hasattr(obs, "expense_report"), "Observation must have expense_report"
        assert hasattr(obs, "receipts"), "Observation must have receipts"
        assert hasattr(obs, "policy"), "Observation must have policy"
        assert hasattr(obs, "step_number"), "Observation must have step_number"
        assert hasattr(obs, "max_steps"), "Observation must have max_steps"
        assert hasattr(obs, "previous_findings"), "Observation must have previous_findings"
        assert hasattr(obs, "message"), "Observation must have message"
        
        # Verify initial state
        assert obs.step_number == 0, "Initial step number must be 0"
        assert obs.max_steps == 20, "Max steps must be 20"
        assert len(obs.previous_findings) == 0, "Initial findings must be empty"
        
        # Verify policy structure
        policy = obs.policy
        assert hasattr(policy, "meal_limit_per_person"), "Policy must have meal_limit_per_person"
        assert hasattr(policy, "hotel_limit_per_night"), "Policy must have hotel_limit_per_night"
        assert hasattr(policy, "requires_receipt_above"), "Policy must have requires_receipt_above"
        assert hasattr(policy, "max_advance_days"), "Policy must have max_advance_days"
        assert hasattr(policy, "no_alcohol_reimbursement"), "Policy must have no_alcohol_reimbursement"
        assert hasattr(policy, "single_approval_limit"), "Policy must have single_approval_limit"
        
        print(f"✓ Environment reset for {task_id}: PASS")


def test_environment_step_behavior():
    """
    Verify environment step produces consistent observations and rewards.
    
    **Preservation Requirement 3.1**: Environment step/reset/state logic and
    reward calculations must remain unchanged.
    """
    env = ReceiptReconciliationEnv()
    
    # Test with task_easy
    obs = env.reset(task_id="task_easy")
    
    # Take a flag_discrepancy action
    action = Action(
        action_type=ActionType.FLAG_DISCREPANCY,
        item_id="E001",
        finding_type=FindingType.AMOUNT_MISMATCH,
        description="Test finding",
        severity=Severity.HIGH,
        confidence=0.9
    )
    
    obs, reward, done, info = env.step(action)
    
    # Verify response structure
    assert hasattr(obs, "step_number"), "Observation must have step_number"
    assert obs.step_number == 1, "Step number must increment"
    assert hasattr(reward, "value"), "Reward must have value"
    assert isinstance(done, bool), "Done must be boolean"
    assert isinstance(info, dict), "Info must be dict"
    
    # Verify reward structure
    assert hasattr(reward, "breakdown"), "Reward must have breakdown"
    
    print("✓ Environment step behavior: PASS")


def test_environment_state_method():
    """
    Verify environment state() method returns complete state.
    
    **Preservation Requirement 3.1**: Environment state logic must remain unchanged.
    """
    env = ReceiptReconciliationEnv()
    obs = env.reset(task_id="task_easy")
    
    state = env.state()
    
    # Verify state structure (actual implementation uses "step" not "step_number")
    assert isinstance(state, dict), "State must be a dict"
    assert "task_id" in state, "State must contain task_id"
    assert "step" in state, "State must contain step"
    assert "done" in state, "State must contain done"
    assert "submitted" in state, "State must contain submitted"
    assert "findings" in state, "State must contain findings"
    
    print("✓ Environment state method: PASS")


def test_api_endpoint_structure():
    """
    Verify API endpoints return expected response formats.
    
    **Preservation Requirement 3.2**: API endpoints (/health, /tasks, /reset, /step, /state)
    must continue to return the same response formats and status codes.
    
    Note: This test verifies the structure without actually starting a server.
    """
    # We can't easily test the actual HTTP endpoints without starting a server,
    # but we can verify the environment behavior that the API wraps
    
    env = ReceiptReconciliationEnv()
    
    # Simulate /reset endpoint
    obs = env.reset(task_id="task_easy")
    obs_dict = obs.model_dump()
    assert isinstance(obs_dict, dict), "Reset response must be dict"
    assert "task_id" in obs_dict, "Reset response must contain task_id"
    
    # Simulate /step endpoint
    action = Action(
        action_type=ActionType.REQUEST_INFO,
        description="Test request"
    )
    obs, reward, done, info = env.step(action)
    
    step_response = {
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info,
    }
    
    assert "observation" in step_response, "Step response must contain observation"
    assert "reward" in step_response, "Step response must contain reward"
    assert "done" in step_response, "Step response must contain done"
    assert "info" in step_response, "Step response must contain info"
    
    # Simulate /state endpoint
    state = env.state()
    assert isinstance(state, dict), "State response must be dict"
    
    print("✓ API endpoint structure: PASS")


def test_inference_log_format():
    """
    Verify inference.py produces correct [START], [STEP], [END] log format.
    
    **Preservation Requirement 3.4**: inference.py must continue to run the three tasks
    and produce the same [START], [STEP], [END] log format with identical semantics.
    
    Note: We test the log format structure without actually running the full inference
    since it requires API server and LLM access.
    """
    # Verify the log format patterns exist in inference.py
    inference_path = Path("receipt-reconciliation/inference.py")
    if not inference_path.exists():
        inference_path = Path("inference.py")
    
    assert inference_path.exists(), "inference.py must exist"
    
    with open(inference_path) as f:
        content = f.read()
    
    # Verify log format functions exist
    assert "[START]" in content, "inference.py must contain [START] log format"
    assert "[STEP]" in content, "inference.py must contain [STEP] log format"
    assert "[END]" in content, "inference.py must contain [END] log format"
    
    # Verify log functions are defined
    assert "def log_start" in content, "inference.py must define log_start function"
    assert "def log_step" in content, "inference.py must define log_step function"
    assert "def log_end" in content, "inference.py must define log_end function"
    
    # Verify task list
    assert "task_easy" in content, "inference.py must reference task_easy"
    assert "task_medium" in content, "inference.py must reference task_medium"
    assert "task_hard" in content, "inference.py must reference task_hard"
    
    print("✓ Inference log format: PASS")


def test_environment_variables():
    """
    Verify environment variables work with expected defaults.
    
    **Preservation Requirement 3.5**: Environment variables (HF_TOKEN, API_BASE_URL,
    MODEL_NAME, ENV_BASE_URL) must continue to work with the same defaults.
    """
    inference_path = Path("receipt-reconciliation/inference.py")
    if not inference_path.exists():
        inference_path = Path("inference.py")
    
    with open(inference_path) as f:
        content = f.read()
    
    # Verify environment variables are referenced
    assert "HF_TOKEN" in content, "inference.py must reference HF_TOKEN"
    assert "API_BASE_URL" in content, "inference.py must reference API_BASE_URL"
    assert "MODEL_NAME" in content, "inference.py must reference MODEL_NAME"
    assert "ENV_BASE_URL" in content, "inference.py must reference ENV_BASE_URL"
    
    # Verify defaults
    assert "https://router.huggingface.co/v1" in content, "API_BASE_URL default must be preserved"
    assert "Qwen/Qwen2.5-72B-Instruct" in content, "MODEL_NAME default must be preserved"
    assert "http://localhost:7860" in content, "ENV_BASE_URL default must be preserved"
    
    print("✓ Environment variables: PASS")


def test_openenv_yaml_metadata():
    """
    Verify openenv.yaml describes the same tasks, observation space, and action space.
    
    **Preservation Requirement 3.6**: openenv.yaml metadata must continue to describe
    the same tasks, observation space, and action space.
    """
    openenv_path = Path("receipt-reconciliation/openenv.yaml")
    assert openenv_path.exists(), "openenv.yaml must exist in receipt-reconciliation/"
    
    import yaml
    with open(openenv_path) as f:
        config = yaml.safe_load(f)
    
    # Verify structure
    assert "tasks" in config, "openenv.yaml must contain tasks"
    assert "observation_space" in config, "openenv.yaml must contain observation_space"
    assert "action_space" in config, "openenv.yaml must contain action_space"
    
    # Verify tasks
    tasks = config["tasks"]
    assert isinstance(tasks, list), "tasks must be a list"
    assert len(tasks) == 3, "Must have 3 tasks"
    
    task_ids = [t["id"] for t in tasks]
    assert "task_easy" in task_ids, "Must have task_easy"
    assert "task_medium" in task_ids, "Must have task_medium"
    assert "task_hard" in task_ids, "Must have task_hard"
    
    # Verify observation space (actual structure uses "fields" not direct keys)
    obs_space = config["observation_space"]
    assert "fields" in obs_space or "task_id" in str(obs_space), \
        "observation_space must describe task_id field"
    
    # Verify action space
    action_space = config["action_space"]
    assert "fields" in action_space or "action_type" in str(action_space), \
        "action_space must describe action_type field"
    
    print("✓ OpenEnv YAML metadata: PASS")


def test_task_definitions():
    """
    Verify task definitions remain unchanged.
    
    **Preservation Requirement 3.1**: Task definitions and grading logic must remain unchanged.
    """
    from environment.tasks import TASKS
    
    # Verify all three tasks exist
    assert "task_easy" in TASKS, "task_easy must exist"
    assert "task_medium" in TASKS, "task_medium must exist"
    assert "task_hard" in TASKS, "task_hard must exist"
    
    # Verify task_easy structure
    task_easy = TASKS["task_easy"]
    assert "expense_report" in task_easy, "task_easy must have expense_report"
    assert "receipts" in task_easy, "task_easy must have receipts"
    assert "ground_truth" in task_easy, "task_easy must have ground_truth"
    
    # Verify ground_truth structure
    gt = task_easy["ground_truth"]
    assert "required_findings" in gt, "ground_truth must have required_findings"
    
    # Verify task_easy has the expected single item
    assert len(task_easy["expense_report"]) == 1, "task_easy must have 1 expense item"
    assert len(task_easy["receipts"]) == 1, "task_easy must have 1 receipt"
    
    print("✓ Task definitions: PASS")


if __name__ == "__main__":
    print("Running Preservation Property Tests...")
    print("=" * 70)
    print("These tests capture baseline behavior that must be preserved")
    print("=" * 70)
    print()
    
    tests = [
        ("Environment reset behavior", test_environment_reset_behavior),
        ("Environment step behavior", test_environment_step_behavior),
        ("Environment state method", test_environment_state_method),
        ("API endpoint structure", test_api_endpoint_structure),
        ("Inference log format", test_inference_log_format),
        ("Environment variables", test_environment_variables),
        ("OpenEnv YAML metadata", test_openenv_yaml_metadata),
        ("Task definitions", test_task_definitions),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            test_func()
            results.append((test_name, "PASS", None))
        except AssertionError as e:
            results.append((test_name, "FAIL", str(e)))
            print(f"✗ {test_name}: FAIL")
            print(f"  Error: {e}")
        except Exception as e:
            results.append((test_name, "ERROR", str(e)))
            print(f"✗ {test_name}: ERROR")
            print(f"  Error: {e}")
        print()
    
    print("=" * 70)
    print("Summary:")
    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = sum(1 for _, status, _ in results if status == "FAIL")
    errors = sum(1 for _, status, _ in results if status == "ERROR")
    print(f"Passed: {passed}, Failed: {failed}, Errors: {errors}")
    print("=" * 70)
    
    sys.exit(0 if failed == 0 and errors == 0 else 1)
