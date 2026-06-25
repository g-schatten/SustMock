"""Rule-based CRM ticket classifier for QueueStorm warmup."""

from __future__ import annotations

import re
from dataclasses import dataclass


CASE_TYPES = (
    "wrong_transfer",
    "payment_failed",
    "refund_request",
    "phishing_or_social_engineering",
    "other",
)

SEVERITIES = ("low", "medium", "high", "critical")
DEPARTMENTS = (
    "customer_support",
    "dispute_resolution",
    "payments_ops",
    "fraud_risk",
)


@dataclass(frozen=True)
class Classification:
    case_type: str
    severity: str
    department: str
    agent_summary: str
    human_review_required: bool
    confidence: float


PHISHING_PATTERNS = [
    r"\botp\b",
    r"\bpin\b",
    r"\bpassword\b",
    r"\bpasscode\b",
    r"\bcard\s*number\b",
    r"\bfull\s*card\b",
    r"\bcvv\b",
    r"\bscam\b",
    r"\bfraud\b",
    r"\bfake\s*call\b",
    r"\bsuspicious\s*call\b",
    r"\bsuspicious\s*sms\b",
    r"\bphishing\b",
    r"\bsocial\s*engineering\b",
    r"asking\s+(for\s+)?my\s+(otp|pin|password)",
    r"share\s+(your\s+)?(otp|pin|password)",
]

WRONG_TRANSFER_PATTERNS = [
    r"wrong\s+(number|account|recipient|person|mobile|phone)",
    r"sent\s+.*\s+to\s+(a\s+)?wrong",
    r"transferred\s+.*\s+wrong",
    r"mistaken\s+transfer",
    r"incorrect\s+(number|account|recipient)",
    r"ভুল\s+নম্বর",
    r"ভুল\s+নাম্বার",
    r"ভুল\s+অ্যাকাউন্ট",
]

PAYMENT_FAILED_PATTERNS = [
    r"payment\s+failed",
    r"transaction\s+failed",
    r"failed\s+payment",
    r"failed\s+transaction",
    r"payment\s+did\s+not\s+go\s+through",
    r"balance\s+deducted",
    r"money\s+deducted",
    r"amount\s+deducted",
    r"charged\s+but",
    r"debited\s+but",
    r"পেমেন্ট\s+ফেইল",
    r"লেনদেন\s+ব্যর্থ",
]

REFUND_PATTERNS = [
    r"\brefund\b",
    r"money\s+back",
    r"return\s+my\s+money",
    r"reverse\s+(the\s+)?transaction",
    r"cancel\s+(my\s+)?(last\s+)?transaction",
    r"changed\s+my\s+mind",
    r"রিফান্ড",
    r"টাকা\s+ফেরত",
]

CONTESTED_REFUND_PATTERNS = [
    r"did\s+not\s+receive",
    r"never\s+received",
    r"not\s+received",
    r"dispute",
    r"contested",
    r"unauthorized",
    r"didn'?t\s+authorize",
    r"without\s+permission",
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def _extract_amount(text: str) -> str | None:
    match = re.search(
        r"(\d[\d,]*(?:\.\d+)?)\s*(?:taka|tk|bdt|৳)?",
        text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1).replace(",", "")
    return None


def _build_summary(
    case_type: str,
    message: str,
    severity: str,
) -> str:
    amount = _extract_amount(message)
    amount_part = f"{amount} BDT " if amount else ""

    summaries = {
        "wrong_transfer": (
            f"Customer reports sending {amount_part}to a wrong recipient and requests recovery."
            if amount
            else "Customer reports sending money to a wrong recipient and requests recovery."
        ),
        "payment_failed": (
            f"Customer reports a failed payment with possible balance deduction ({amount_part.strip()})."
            if amount
            else "Customer reports a failed payment with possible balance deduction."
        ),
        "refund_request": (
            "Customer requests a refund for a recent transaction."
            if severity != "high"
            else "Customer disputes a transaction and requests a refund or reversal."
        ),
        "phishing_or_social_engineering": (
            "Customer reports suspicious contact attempting to obtain sensitive credentials."
        ),
        "other": "Customer reports a general app or service issue unrelated to payments or fraud.",
    }
    return summaries[case_type]


def _department_for(case_type: str, severity: str, contested_refund: bool) -> str:
    if case_type == "phishing_or_social_engineering":
        return "fraud_risk"
    if case_type == "payment_failed":
        return "payments_ops"
    if case_type == "wrong_transfer":
        return "dispute_resolution"
    if case_type == "refund_request":
        if contested_refund or severity in {"high", "critical"}:
            return "dispute_resolution"
        return "customer_support"
    return "customer_support"


def _severity_for(case_type: str, contested_refund: bool) -> str:
    if case_type == "phishing_or_social_engineering":
        return "critical"
    if case_type == "wrong_transfer":
        return "high"
    if case_type == "payment_failed":
        return "high"
    if case_type == "refund_request":
        return "high" if contested_refund else "low"
    return "low"


def _confidence_for(case_type: str, matched_primary: bool) -> float:
    if not matched_primary:
        return 0.55
    if case_type == "other":
        return 0.65
    if case_type == "phishing_or_social_engineering":
        return 0.92
    return 0.85


def classify_ticket(message: str) -> Classification:
    text = _normalize(message)

    if _matches_any(text, PHISHING_PATTERNS):
        case_type = "phishing_or_social_engineering"
        contested = False
    elif _matches_any(text, WRONG_TRANSFER_PATTERNS):
        case_type = "wrong_transfer"
        contested = False
    elif _matches_any(text, PAYMENT_FAILED_PATTERNS):
        case_type = "payment_failed"
        contested = False
    elif _matches_any(text, REFUND_PATTERNS):
        case_type = "refund_request"
        contested = _matches_any(text, CONTESTED_REFUND_PATTERNS)
    else:
        case_type = "other"
        contested = False

    severity = _severity_for(case_type, contested)
    department = _department_for(case_type, severity, contested)
    agent_summary = _build_summary(case_type, text, severity)
    human_review_required = (
        severity == "critical" or case_type == "phishing_or_social_engineering"
    )
    confidence = _confidence_for(case_type, case_type != "other")

    return Classification(
        case_type=case_type,
        severity=severity,
        department=department,
        agent_summary=agent_summary,
        human_review_required=human_review_required,
        confidence=confidence,
    )
