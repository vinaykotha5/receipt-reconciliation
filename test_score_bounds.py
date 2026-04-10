"""Test that all grader scores are strictly within (0, 1)."""
import sys
sys.path.insert(0, 'receipt-reconciliation')

from environment.tasks import grade, safe_score
from environment.models import Finding, FindingType, Severity

def check(label, score):
    ok = 0 < score < 1
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}: score={score}")
    assert ok, f"Score {score} not strictly in (0,1)"

print("=== safe_score edge cases ===")
for v in [0.0, 1.0, -0.5, 1.5, 0.5, 0.01, 0.99]:
    s = safe_score(v)
    check(f"safe_score({v})", s)

print("\n=== Grader: Empty findings (no submit) ===")
for tid in ["task_easy", "task_medium", "task_hard"]:
    r = grade(tid, [])
    check(f"{tid} empty/no-submit", r["score"])

print("\n=== Grader: Empty findings (with submit) ===")
for tid in ["task_easy", "task_medium", "task_hard"]:
    r = grade(tid, [], submitted=True)
    check(f"{tid} empty/submit", r["score"])

print("\n=== Grader: Perfect easy task ===")
findings = [
    Finding(item_id="E001", finding_type=FindingType.AMOUNT_MISMATCH,
            severity=Severity.HIGH, description="Amount mismatch", confidence=1.0),
    Finding(item_id="E001", finding_type=FindingType.POLICY_VIOLATION,
            severity=Severity.MEDIUM, description="Policy violation", confidence=0.9),
]
r = grade("task_easy", findings, submitted=True)
check("task_easy perfect/submit", r["score"])

print("\n=== Grader: Perfect medium task ===")
findings_med = [
    Finding(item_id="E005", finding_type=FindingType.DUPLICATE,
            severity=Severity.HIGH, description="Dup", confidence=1.0),
    Finding(item_id="E003", finding_type=FindingType.POLICY_VIOLATION,
            severity=Severity.HIGH, description="Alcohol", confidence=1.0),
    Finding(item_id="E004", finding_type=FindingType.MISSING_RECEIPT,
            severity=Severity.MEDIUM, description="Missing", confidence=0.9),
    Finding(item_id="E003", finding_type=FindingType.VENDOR_MISMATCH,
            severity=Severity.MEDIUM, description="Vendor", confidence=0.8),
    Finding(item_id="E001", finding_type=FindingType.POLICY_VIOLATION,
            severity=Severity.MEDIUM, description="Hotel", confidence=0.8),
]
r = grade("task_medium", findings_med, submitted=True)
check("task_medium perfect/submit", r["score"])

print("\n=== Grader: Perfect hard task ===")
findings_hard = [
    Finding(item_id="E001", finding_type=FindingType.SUSPICIOUS_PATTERN,
            severity=Severity.CRITICAL, description="Split", confidence=1.0),
    Finding(item_id="E002", finding_type=FindingType.SUSPICIOUS_PATTERN,
            severity=Severity.CRITICAL, description="Split", confidence=1.0),
    Finding(item_id="E003", finding_type=FindingType.SUSPICIOUS_PATTERN,
            severity=Severity.CRITICAL, description="Personal", confidence=1.0),
    Finding(item_id="E004", finding_type=FindingType.AMOUNT_MISMATCH,
            severity=Severity.HIGH, description="Inflate", confidence=1.0),
    Finding(item_id="E006", finding_type=FindingType.DUPLICATE,
            severity=Severity.HIGH, description="Dup", confidence=1.0),
    Finding(item_id="E007", finding_type=FindingType.MISSING_RECEIPT,
            severity=Severity.MEDIUM, description="Missing", confidence=1.0),
    Finding(item_id="E010", finding_type=FindingType.POLICY_VIOLATION,
            severity=Severity.HIGH, description="Stale", confidence=1.0),
    Finding(item_id="E008", finding_type=FindingType.POLICY_VIOLATION,
            severity=Severity.MEDIUM, description="Meal limit", confidence=0.9),
    Finding(item_id="E004", finding_type=FindingType.POLICY_VIOLATION,
            severity=Severity.HIGH, description="Hotel limit", confidence=0.9),
]
r = grade("task_hard", findings_hard, submitted=True)
check("task_hard perfect/submit", r["score"])

print("\n=== All tests passed! ===")
