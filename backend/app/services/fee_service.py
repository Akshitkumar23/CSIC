"""Student fee billing and online payment processing service."""
from typing import Any, Optional

from fastapi import HTTPException, status

from backend.app.models.fee import FeePayment, FeeSummary
from backend.app.repositories.database import get_repository


class FeeService:
    """Manages student tuition invoices and online payment transactions."""

    def __init__(self, repo: Optional[Any] = None) -> None:
        self.repo = repo or get_repository()

    def get_summary(self, student_id: str) -> FeeSummary:
        """Fetch invoice balances and payment transaction history."""
        summary = self.repo.get_fee_summary(student_id)
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fee invoices not found for student '{student_id}'",
            )
        return summary

    def process_payment(
        self,
        invoice_id: str,
        amount_paid: float,
        payment_method: str = "upi",
    ) -> FeePayment:
        """Record an approved payment towards an invoice."""
        payment = self.repo.record_fee_payment(invoice_id, amount_paid, payment_method)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice '{invoice_id}' not found",
            )
        return payment


fee_service = FeeService()
