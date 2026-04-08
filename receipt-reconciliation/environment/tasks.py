"""
Task definitions and agent graders for Receipt Reconciliation Investigator.
Each task has:
  - seed data (expense report + receipts + policy)
  - ground_truth: the set of issues the agent must find
  - grader: deterministic 0.0–1.0 scoring function
"""

from typing import Dict, Any, List
from environment.models import (
    ExpenseLineItem, Receipt, ExpensePolicy, Finding,
    FindingType, Severity
)


# ══════════════════════════════════════════════════════════════════════════════
# TASK 1 — EASY: Single receipt, one clear mismatch
# ══════════════════════════════════════════════════════════════════════════════

TASK_EASY = {
    "task_id": "task_easy",
    "expense_report": [
        ExpenseLineItem(
            item_id="E001",
            date="2024-03-15",
            vendor="The Capital Grille",
            amount=124.50,
            category="meals",
            description="Client lunch with John Smith (Acme Corp)",
            receipt_id="R001"
        )
    ],
    "receipts": [
        Receipt(
            receipt_id="R001",
            date="2024-03-15",
            vendor="The Capital Grille",
            amount=98.50,          # ← claimed $124.50 but receipt says $98.50
            items=["Steak $45", "Salmon $38", "Dessert $15.50"],
            tax=8.25,
            tip=0.0                # tip was NOT on receipt (paid separately/personal)
        )
    ],
    "policy": ExpensePolicy(),
    "ground_truth": {
        "required_findings": [
            {
                "item_id": "E001",
                "finding_type": FindingType.AMOUNT_MISMATCH,
                "severity": Severity.HIGH,
                "note": "Claimed $124.50 vs receipt $98.50 — $26 overage"
            }
        ],
        "optional_findings": [
            {
                "item_id": "E001",
                "finding_type": FindingType.POLICY_VIOLATION,
                "note": "Receipt has no tip; $26 gap suggests undisclosed tip reimbursement attempt"
            }
        ],
        "false_positive_penalty_items": []   # nothing else is wrong
    }
}


# ══════════════════════════════════════════════════════════════════════════════
# TASK 2 — MEDIUM: 5-item expense report, multiple issue types
# ══════════════════════════════════════════════════════════════════════════════

TASK_MEDIUM = {
    "task_id": "task_medium",
    "expense_report": [
        ExpenseLineItem(
            item_id="E001",
            date="2024-04-02",
            vendor="Marriott Downtown",
            amount=289.00,
            category="hotel",
            description="Hotel night — client visit Chicago",
            receipt_id="R001"
        ),
        ExpenseLineItem(
            item_id="E002",
            date="2024-04-03",
            vendor="Uber",
            amount=34.20,
            category="transport",
            description="Ride to airport",
            receipt_id="R002"
        ),
        ExpenseLineItem(
            item_id="E003",
            date="2024-04-03",
            vendor="O'Hare Airport Lounge",
            amount=65.00,
            category="meals",
            description="Airport meal",
            receipt_id="R003"
        ),
        ExpenseLineItem(
            item_id="E004",
            date="2024-04-05",
            vendor="Starbucks",
            amount=18.40,
            category="meals",
            description="Coffee with client",
            receipt_id=None           # ← no receipt provided
        ),
        ExpenseLineItem(
            item_id="E005",
            date="2024-04-03",    # ← same date as E002 / same vendor
            vendor="Uber",
            amount=34.20,
            category="transport",
            description="Ride to client office",
            receipt_id="R002"         # ← same receipt_id as E002 — duplicate!
        ),
    ],
    "receipts": [
        Receipt(
            receipt_id="R001",
            date="2024-04-02",
            vendor="Marriott Downtown",
            amount=289.00,
            items=["Room rate $265", "Parking $24"],
            tax=0.0,
            tip=0.0
        ),
        Receipt(
            receipt_id="R002",
            date="2024-04-03",
            vendor="Uber",
            amount=34.20,
            items=["Trip fare"],
            tax=0.0,
            tip=0.0
        ),
        Receipt(
            receipt_id="R003",
            date="2024-04-03",
            vendor="O'Hare Lounge Bar",   # ← vendor name mismatch + has "Bar"
            amount=65.00,
            items=["Food $32", "Wine $18", "Beer $15"],   # ← alcohol present
            tax=0.0,
            tip=0.0
        ),
    ],
    "policy": ExpensePolicy(),
    "ground_truth": {
        "required_findings": [
            {
                "item_id": "E005",
                "finding_type": FindingType.DUPLICATE,
                "severity": Severity.HIGH,
                "note": "E005 reuses receipt R002 already claimed by E002"
            },
            {
                "item_id": "E003",
                "finding_type": FindingType.POLICY_VIOLATION,
                "severity": Severity.HIGH,
                "note": "Receipt R003 contains alcohol (wine $18, beer $15) — policy prohibits reimbursement"
            },
            {
                "item_id": "E004",
                "finding_type": FindingType.MISSING_RECEIPT,
                "severity": Severity.MEDIUM,
                "note": "E004 ($18.40) has no receipt_id — policy requires receipt above $25... but amount is under $25, so this is optional"
            },
        ],
        "optional_findings": [
            {
                "item_id": "E003",
                "finding_type": FindingType.VENDOR_MISMATCH,
                "note": "Claimed vendor 'O'Hare Airport Lounge' vs receipt 'O'Hare Lounge Bar'"
            },
            {
                "item_id": "E001",
                "finding_type": FindingType.POLICY_VIOLATION,
                "note": "Hotel $289 exceeds $250/night policy limit"
            }
        ],
        "false_positive_penalty_items": ["E002"]  # E002 is clean — penalise if flagged
    }
}


# ══════════════════════════════════════════════════════════════════════════════
# TASK 3 — HARD: 10-item report with subtle fraud patterns
# ══════════════════════════════════════════════════════════════════════════════

TASK_HARD = {
    "task_id": "task_hard",
    "expense_report": [
        # Split transaction to stay under $500 approval threshold
        ExpenseLineItem(
            item_id="E001",
            date="2024-05-10",
            vendor="Adobe Systems",
            amount=490.00,
            category="software",
            description="Annual Adobe Creative Cloud license",
            receipt_id="R001"
        ),
        ExpenseLineItem(
            item_id="E002",
            date="2024-05-10",
            vendor="Adobe Systems",
            amount=490.00,
            category="software",
            description="Adobe Stock annual plan",
            receipt_id="R002"
        ),
        # Personal dinner disguised as business meal
        ExpenseLineItem(
            item_id="E003",
            date="2024-05-11",
            vendor="Nobu Restaurant",
            amount=340.00,
            category="meals",
            description="Team dinner — Q2 planning (4 attendees)",
            receipt_id="R003"
        ),
        # Inflated hotel — claimed $310, receipt shows $210
        ExpenseLineItem(
            item_id="E004",
            date="2024-05-12",
            vendor="Hyatt Regency",
            amount=310.00,
            category="hotel",
            description="Hotel — SF conference",
            receipt_id="R004"
        ),
        # Legitimate transport
        ExpenseLineItem(
            item_id="E005",
            date="2024-05-12",
            vendor="Lyft",
            amount=42.00,
            category="transport",
            description="Ride to conference",
            receipt_id="R005"
        ),
        # Duplicate of E005 with date shifted by one day
        ExpenseLineItem(
            item_id="E006",
            date="2024-05-13",    # ← shifted by 1 day vs E005
            vendor="Lyft",
            amount=42.00,
            category="transport",
            description="Ride from conference",
            receipt_id="R006"
        ),
        # Missing receipt, above threshold
        ExpenseLineItem(
            item_id="E007",
            date="2024-05-13",
            vendor="FedEx",
            amount=87.50,
            category="office",
            description="Overnight shipment of contract documents",
            receipt_id=None
        ),
        # Policy violation: meal per-person exceeds limit
        # $340 / 4 = $85/person > $75 policy limit
        ExpenseLineItem(
            item_id="E008",
            date="2024-05-14",
            vendor="Morton's Steakhouse",
            amount=320.00,
            category="meals",
            description="Client dinner (4 attendees)",
            receipt_id="R008"
        ),
        # Legitimate office supply
        ExpenseLineItem(
            item_id="E009",
            date="2024-05-15",
            vendor="Staples",
            amount=54.30,
            category="office",
            description="Printer paper and toner",
            receipt_id="R009"
        ),
        # Old claim — outside 90-day policy window
        ExpenseLineItem(
            item_id="E010",
            date="2024-01-15",   # ← ~120 days old (filed May 2024)
            vendor="Delta Airlines",
            amount=425.00,
            category="travel",
            description="Flight to NYC — January conference",
            receipt_id="R010"
        ),
    ],
    "receipts": [
        Receipt(receipt_id="R001", date="2024-05-10", vendor="Adobe Systems",
                amount=490.00, items=["Creative Cloud Business $490"]),
        Receipt(receipt_id="R002", date="2024-05-10", vendor="Adobe Systems",
                amount=490.00, items=["Adobe Stock Business $490"]),
        Receipt(receipt_id="R003", date="2024-05-11", vendor="Nobu Restaurant",
                amount=340.00, items=["Omakase x2 $280", "Sake $60"],
                tip=0.0),   # only 2 omakase — not 4 people
        Receipt(receipt_id="R004", date="2024-05-12", vendor="Hyatt Regency",
                amount=210.00, items=["Room rate $210"]),    # ← $100 less than claimed
        Receipt(receipt_id="R005", date="2024-05-12", vendor="Lyft",
                amount=42.00, items=["Trip fare $42"]),
        Receipt(receipt_id="R006", date="2024-05-12", vendor="Lyft",   # ← same date as R005
                amount=42.00, items=["Trip fare $42"]),
        Receipt(receipt_id="R008", date="2024-05-14", vendor="Morton's Steakhouse",
                amount=320.00, items=["Steaks x4 $240", "Wine $55", "Dessert $25"],
                tip=0.0),
        Receipt(receipt_id="R009", date="2024-05-15", vendor="Staples",
                amount=54.30, items=["Paper $22.50", "Toner $31.80"]),
        Receipt(receipt_id="R010", date="2024-01-15", vendor="Delta Airlines",
                amount=425.00, items=["Flight JFK-SFO $425"]),
    ],
    "policy": ExpensePolicy(),
    "ground_truth": {
        "required_findings": [
            {
                "item_id": "E001",
                "finding_type": FindingType.SUSPICIOUS_PATTERN,
                "severity": Severity.CRITICAL,
                "note": "E001+E002 same vendor same day both $490 — classic split to avoid $500 approval threshold"
            },
            {
                "item_id": "E002",
                "finding_type": FindingType.SUSPICIOUS_PATTERN,
                "severity": Severity.CRITICAL,
                "note": "Same as E001 — part of split transaction pattern"
            },
            {
                "item_id": "E003",
                "finding_type": FindingType.SUSPICIOUS_PATTERN,
                "severity": Severity.CRITICAL,
                "note": "Receipt shows only 2 omakase covers but claims 4 attendees — likely personal dinner"
            },
            {
                "item_id": "E004",
                "finding_type": FindingType.AMOUNT_MISMATCH,
                "severity": Severity.HIGH,
                "note": "Claimed $310 but receipt shows $210 — $100 inflation"
            },
            {
                "item_id": "E006",
                "finding_type": FindingType.DUPLICATE,
                "severity": Severity.HIGH,
                "note": "R006 same vendor/amount as R005 but date shifted by 1 day — likely duplicate"
            },
            {
                "item_id": "E007",
                "finding_type": FindingType.MISSING_RECEIPT,
                "severity": Severity.MEDIUM,
                "note": "$87.50 above $25 receipt threshold — no receipt provided"
            },
            {
                "item_id": "E010",
                "finding_type": FindingType.POLICY_VIOLATION,
                "severity": Severity.HIGH,
                "note": "Jan 15 claim filed ~120 days later — exceeds 90-day submission policy"
            },
        ],
        "optional_findings": [
            {
                "item_id": "E008",
                "finding_type": FindingType.POLICY_VIOLATION,
                "note": "$320/4 = $80/person exceeds $75 meal limit"
            },
            {
                "item_id": "E008",
                "finding_type": FindingType.POLICY_VIOLATION,
                "note": "Receipt includes wine — alcohol not reimbursable"
            },
            {
                "item_id": "E004",
                "finding_type": FindingType.POLICY_VIOLATION,
                "note": "Even at face value $310 exceeds $250/night hotel limit"
            },
        ],
        "false_positive_penalty_items": ["E005", "E009"]  # these are clean
    }
}

TASKS: Dict[str, Any] = {
    "task_easy":   TASK_EASY,
    "task_medium": TASK_MEDIUM,
    "task_hard":   TASK_HARD,
}


# ══════════════════════════════════════════════════════════════════════════════
# GRADER
# ══════════════════════════════════════════════════════════════════════════════

def grade(task_id: str, findings: List[Finding]) -> Dict[str, Any]:
    """
    Deterministic grader. Returns score 0.0–1.0 with breakdown.

    Scoring logic:
      - required_recall:   fraction of required findings correctly identified  (weight 0.55)
      - optional_bonus:    bonus for optional findings caught                  (weight 0.15)
      - false_positive_penalty: penalise flagging clean items                 (weight -0.20)
      - confidence_quality: average confidence calibration on true positives  (weight 0.10)
      - submit_bonus:       small bonus if agent explicitly submits a report   (weight 0.05)
    """
    task = TASKS[task_id]
    gt   = task["ground_truth"]

    required  = gt["required_findings"]
    optional  = gt.get("optional_findings", [])
    fp_items  = set(gt.get("false_positive_penalty_items", []))

    # Index agent findings by (item_id, finding_type)
    agent_flags: Dict[str, set] = {}
    has_submit  = False
    confidence_scores = []

    for f in findings:
        key = f.item_id
        if key not in agent_flags:
            agent_flags[key] = set()
        agent_flags[key].add(f.finding_type)
        if f.finding_type != FindingType.APPROVED:
            confidence_scores.append(f.confidence)

    # Check if agent submitted a report
    for f in findings:
        if hasattr(f, "_submitted") and f._submitted:
            has_submit = True

    # Required recall
    req_hit = 0
    for req in required:
        item_findings = agent_flags.get(req["item_id"], set())
        if req["finding_type"] in item_findings:
            req_hit += 1
    recall = req_hit / max(len(required), 1)

    # Optional bonus (each worth a fraction)
    opt_hit = 0
    for opt in optional:
        item_findings = agent_flags.get(opt["item_id"], set())
        if opt["finding_type"] in item_findings:
            opt_hit += 1
    opt_bonus = min(opt_hit / max(len(optional), 1), 1.0) if optional else 0.0

    # False positive penalty
    fp_count = 0
    for item_id, ftypes in agent_flags.items():
        if item_id in fp_items:
            fp_count += len(ftypes)
    max_fp = max(len(fp_items) * 2, 1)
    fp_penalty = min(fp_count / max_fp, 1.0)

    # Confidence quality (reward high confidence on true positives)
    conf_quality = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5

    # Final score
    score = (
        0.55 * recall
        + 0.15 * opt_bonus
        - 0.20 * fp_penalty
        + 0.10 * conf_quality
        + (0.05 if has_submit else 0.0)
    )
    score = max(0.0, min(1.0, round(score, 4)))

    return {
        "score":          score,
        "required_recall": round(recall, 4),
        "required_found":  req_hit,
        "required_total":  len(required),
        "optional_found":  opt_hit,
        "optional_total":  len(optional),
        "optional_bonus":  round(opt_bonus, 4),
        "false_positives": fp_count,
        "fp_penalty":      round(fp_penalty, 4),
        "conf_quality":    round(conf_quality, 4),
        "submit_bonus":    0.05 if has_submit else 0.0,
    }
