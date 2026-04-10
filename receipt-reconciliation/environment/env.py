"""
Receipt Reconciliation Investigator — OpenEnv Environment
Implements: reset() / step() / state()
"""

from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime

from environment.models import (
    Action, Observation, Reward,
    Finding, FindingType, ActionType, Severity
)
from environment.tasks import TASKS, grade, safe_score


class ReceiptReconciliationEnv:
    """
    OpenEnv-compatible environment for receipt reconciliation investigation.

    Episode flow:
      1. reset(task_id) → Observation          (agent sees full expense report + receipts)
      2. step(action)   → (Observation, Reward, done, info)   (repeated up to max_steps)
         - action_type = flag_discrepancy  → adds a Finding, gives partial reward
         - action_type = approve_item      → marks item clean, gives small reward if correct
         - action_type = request_info      → no state change, costs a step (simulate real workflow)
         - action_type = submit_report     → triggers final grading, ends episode
      3. Episode ends when: submit_report action OR max_steps reached
    """

    MAX_STEPS = 20

    def __init__(self):
        self._task_id: Optional[str]       = None
        self._task_data: Optional[Dict]    = None
        self._findings: List[Finding]      = []
        self._approved: List[str]          = []
        self._step: int                    = 0
        self._done: bool                   = False
        self._submitted: bool              = False
        self._start_time: Optional[str]    = None

    # ── Public API ─────────────────────────────────────────────────────────────

    def reset(self, task_id: str = "task_easy") -> Observation:
        if task_id not in TASKS:
            raise ValueError(f"Unknown task_id '{task_id}'. Choose from: {list(TASKS)}")

        self._task_id   = task_id
        self._task_data = TASKS[task_id]
        self._findings  = []
        self._approved  = []
        self._step      = 0
        self._done      = False
        self._submitted = False
        self._start_time = datetime.utcnow().isoformat()

        return self._build_observation(
            message=f"Task '{task_id}' started. Review the expense report and receipts. "
                    f"Use flag_discrepancy, approve_item, or submit_report actions. "
                    f"You have {self.MAX_STEPS} steps."
        )

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict]:
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")

        self._step += 1
        reward_value = 0.0
        reward_breakdown = {}
        message = ""

        # ── Handle each action type ────────────────────────────────────────────

        if action.action_type == ActionType.FLAG_DISCREPANCY:
            finding = Finding(
                item_id=action.item_id or "unknown",
                finding_type=action.finding_type or FindingType.SUSPICIOUS_PATTERN,
                severity=action.severity or Severity.MEDIUM,
                description=action.description,
                confidence=action.confidence,
            )
            self._findings.append(finding)

            # Partial reward: check if this finding is in the required set
            partial = self._partial_reward_for_finding(finding)
            reward_value    = partial["value"]
            reward_breakdown = partial["breakdown"]
            message = (
                f"Finding recorded for item {finding.item_id} "
                f"({finding.finding_type.value}, severity={finding.severity.value}). "
                f"Partial reward: {reward_value:.3f}."
            )

        elif action.action_type == ActionType.APPROVE_ITEM:
            item_id = action.item_id or ""
            self._approved.append(item_id)

            # Small reward if approving a genuinely clean item; small penalty otherwise
            fp_items = set(self._task_data["ground_truth"].get("false_positive_penalty_items", []))
            required_items = {r["item_id"] for r in self._task_data["ground_truth"]["required_findings"]}
            if item_id in fp_items:
                reward_value = 0.05   # correctly approving a clean item
                message = f"Item {item_id} approved correctly — it is clean."
            elif item_id in required_items:
                reward_value = -0.05  # wrongly approving a flagged item
                message = f"Item {item_id} approved — but this item has issues. Review carefully."
            else:
                reward_value = 0.02
                message = f"Item {item_id} approved."
            reward_breakdown = {"approve_signal": reward_value}

        elif action.action_type == ActionType.REQUEST_INFO:
            # No state change; costs a step
            reward_value = 0.0
            message = f"Info request logged: '{action.description}'. Step used."
            reward_breakdown = {"request_info": 0.0}

        elif action.action_type == ActionType.SUBMIT_REPORT:
            # Final grading
            self._submitted = True
            self._done      = True
            final = grade(self._task_id, self._findings, submitted=True)
            reward_value     = final["score"]
            reward_breakdown = final
            message = (
                f"Report submitted. Final score: {reward_value:.4f}. "
                f"Required findings: {final['required_found']}/{final['required_total']}. "
                f"Optional bonus: {final['optional_bonus']:.3f}. "
                f"False positive penalty: {final['fp_penalty']:.3f}."
            )

        # Check step limit
        if self._step >= self.MAX_STEPS and not self._done:
            self._done = True
            final = grade(self._task_id, self._findings)
            reward_value     = safe_score(final["score"] * 0.85)
            reward_breakdown = {**final, "timeout_penalty": 0.15}
            message += f" [TIMEOUT] Max steps reached. Score capped. Final: {reward_value:.4f}."

        observation = self._build_observation(message=message)
        reward      = Reward(
            value=safe_score(round(reward_value, 4)),
            breakdown=reward_breakdown,
            reason=message
        )
        info = {
            "step":       self._step,
            "done":       self._done,
            "submitted":  self._submitted,
            "task_id":    self._task_id,
            "n_findings": len(self._findings),
        }
        return observation, reward, self._done, info

    def state(self) -> Dict[str, Any]:
        """Return full current state (for debugging / checkpointing)."""
        return {
            "task_id":    self._task_id,
            "step":       self._step,
            "done":       self._done,
            "submitted":  self._submitted,
            "findings":   [f.model_dump() for f in self._findings],
            "approved":   self._approved,
            "start_time": self._start_time,
            "task_data":  {
                "expense_report": [e.model_dump() for e in self._task_data["expense_report"]],
                "receipts":       [r.model_dump() for r in self._task_data["receipts"]],
                "policy":          self._task_data["policy"].model_dump(),
            } if self._task_data else {},
        }

    # ── Internals ──────────────────────────────────────────────────────────────

    def _build_observation(self, message: str = "") -> Observation:
        return Observation(
            task_id=self._task_id or "",
            expense_report=self._task_data["expense_report"] if self._task_data else [],
            receipts=self._task_data["receipts"]       if self._task_data else [],
            policy=self._task_data["policy"]           if self._task_data else None,
            step_number=self._step,
            max_steps=self.MAX_STEPS,
            previous_findings=list(self._findings),
            message=message,
        )

    def _partial_reward_for_finding(self, finding: Finding) -> Dict:
        """
        Award partial reward mid-episode when the agent flags something.
        Rewards correct findings, penalises false positives.
        """
        gt = self._task_data["ground_truth"]
        required  = gt["required_findings"]
        optional  = gt.get("optional_findings", [])
        fp_items  = set(gt.get("false_positive_penalty_items", []))

        is_required = any(
            r["item_id"] == finding.item_id and r["finding_type"] == finding.finding_type
            for r in required
        )
        is_optional = any(
            o["item_id"] == finding.item_id and o["finding_type"] == finding.finding_type
            for o in optional
        )
        is_fp = finding.item_id in fp_items

        if is_required:
            # Scale by confidence: high confidence correct = max reward
            value = 0.10 * finding.confidence
            return {"value": value, "breakdown": {"required_hit": value}}
        elif is_optional:
            value = 0.05 * finding.confidence
            return {"value": value, "breakdown": {"optional_hit": value}}
        elif is_fp:
            return {"value": -0.05, "breakdown": {"false_positive": -0.05}}
        else:
            # Neutral — not in any list (ambiguous)
            return {"value": 0.0, "breakdown": {"neutral": 0.0}}
