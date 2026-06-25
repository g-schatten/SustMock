from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.classifier import classify_ticket

app = FastAPI()


class SortTicketRequest(BaseModel):
    ticket_id: str
    message: str
    channel: Literal["app", "sms", "call_center", "merchant_portal"] | None = None
    locale: Literal["bn", "en", "mixed"] | None = None


class SortTicketResponse(BaseModel):
    ticket_id: str
    case_type: Literal[
        "wrong_transfer",
        "payment_failed",
        "refund_request",
        "phishing_or_social_engineering",
        "other",
    ]
    severity: Literal["low", "medium", "high", "critical"]
    department: Literal[
        "customer_support",
        "dispute_resolution",
        "payments_ops",
        "fraud_risk",
    ]
    agent_summary: str
    human_review_required: bool
    confidence: float = Field(ge=0.0, le=1.0)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/sort-ticket", response_model=SortTicketResponse)
def sort_ticket(payload: SortTicketRequest) -> SortTicketResponse:
    result = classify_ticket(payload.message)
    return SortTicketResponse(
        ticket_id=payload.ticket_id,
        case_type=result.case_type,
        severity=result.severity,
        department=result.department,
        agent_summary=result.agent_summary,
        human_review_required=result.human_review_required,
        confidence=result.confidence,
    )
