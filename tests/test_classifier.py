from app.classifier import classify_ticket


SAMPLE_CASES = [
    (
        "I sent 3000 to wrong number",
        "wrong_transfer",
        "high",
        "dispute_resolution",
        False,
    ),
    (
        "Payment failed but balance deducted",
        "payment_failed",
        "high",
        "payments_ops",
        False,
    ),
    (
        "Someone called asking my OTP, is that bKash?",
        "phishing_or_social_engineering",
        "critical",
        "fraud_risk",
        True,
    ),
    (
        "Please refund my last transaction, I changed my mind",
        "refund_request",
        "low",
        "customer_support",
        False,
    ),
    (
        "App crashed when I opened it",
        "other",
        "low",
        "customer_support",
        False,
    ),
]


def test_sample_cases():
    for message, expected_type, expected_severity, expected_dept, human_review in SAMPLE_CASES:
        result = classify_ticket(message)
        assert result.case_type == expected_type, message
        assert result.severity == expected_severity, message
        assert result.department == expected_dept, message
        assert result.human_review_required == human_review, message
        assert 0 <= result.confidence <= 1


def test_agent_summary_never_requests_sensitive_data():
    result = classify_ticket("Someone asked for my PIN over SMS")
    summary = result.agent_summary.lower()
    assert "share" not in summary
    assert "provide" not in summary
    assert "send your" not in summary
