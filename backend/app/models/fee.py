from datetime import date, datetime
from typing import List
from pydantic import BaseModel, Field


class FeePayment(BaseModel):
    """Transaction record representing payment towards a fee invoice."""
    id: str
    invoice_id: str
    transaction_reference: str
    amount_paid: float = Field(..., gt=0.0)
    payment_date: datetime
    payment_method: str  # upi, net_banking, card, cash, demand_draft
    status: str = "success"  # success, pending, failed


class FeeInvoice(BaseModel):
    """Institutional billing invoice issued to an enrolled student."""
    id: str
    invoice_number: str
    enrollment_id: str
    title: str
    amount: float = Field(..., gt=0.0)
    due_date: date
    status: str = "unpaid"  # unpaid, partially_paid, paid, overdue, cancelled
    created_at: datetime
    payments: List[FeePayment] = Field(default_factory=list)


class FeeSummary(BaseModel):
    """Financial standing overview for a student account."""
    student_id: str
    total_invoiced: float = Field(..., ge=0.0)
    total_paid: float = Field(..., ge=0.0)
    total_outstanding: float = Field(..., ge=0.0)
    invoices: List[FeeInvoice] = Field(default_factory=list)
