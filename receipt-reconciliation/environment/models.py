from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


# ── Enums ──────────────────────────────────────────────────────────────────────

class FindingType(str, Enum):
    AMOUNT_MISMATCH    = "amount_mismatch"
    DATE_MISMATCH      = "date_mismatch"
    VENDOR_MISMATCH    = "vendor_mismatch"
    MISSING_RECEIPT    = "missing_receipt"
    DUPLICATE          = "duplicate"
    POLICY_VIOLATION   = "policy_violation"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    APPROVED           = "approved"

class Severity(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"

class ActionType(str, Enum):
    FLAG_DISCREPANCY = "flag_discrepancy"
    APPROVE_ITEM     = "approve_item"
    REQUEST_INFO     = "request_info"
    SUBMIT_REPORT    = "submit_report"


# ── Domain models ──────────────────────────────────────────────────────────────

class ExpenseLineItem(BaseModel):
    item_id:     str
    date:        str          # ISO 8601 YYYY-MM-DD
    vendor:      str
    amount:      float
    currency:    str = "USD"
    category:    str
    description: str
    receipt_id:  Optional[str] = None   # claimed receipt reference

class Receipt(BaseModel):
    receipt_id:  str
    date:        str
    vendor:      str
    amount:      float
    currency:    str = "USD"
    items:       List[str]    # line items on receipt
    tax:         float = 0.0
    tip:         float = 0.0

class ExpensePolicy(BaseModel):
    meal_limit_per_person:   float = 75.0
    hotel_limit_per_night:   float = 250.0
    requires_receipt_above:  float = 25.0
    max_advance_days:        int   = 90   # how far back claims can go
    no_alcohol_reimbursement: bool = True
    single_approval_limit:   float = 500.0

class Finding(BaseModel):
    item_id:      str
    finding_type: FindingType
    severity:     Severity
    description:  str
    confidence:   float = Field(ge=0.0, le=1.0)
    expected:     Optional[str] = None
    actual:       Optional[str] = None


# ── Action / Observation / Reward ──────────────────────────────────────────────

class Action(BaseModel):
    action_type:  ActionType
    item_id:      Optional[str]         = None
    finding_type: Optional[FindingType] = None
    description:  str
    severity:     Optional[Severity]    = None
    confidence:   float                 = Field(default=0.8, ge=0.0, le=1.0)

class Observation(BaseModel):
    task_id:           str
    expense_report:    List[ExpenseLineItem]
    receipts:          List[Receipt]
    policy:            Optional[ExpensePolicy] = None
    step_number:       int
    max_steps:         int
    previous_findings: List[Finding]    = []
    message:           str              = ""

class Reward(BaseModel):
    value:             float = Field(gt=0.0, lt=1.0)
    breakdown:         dict  = {}
    reason:            str   = ""
