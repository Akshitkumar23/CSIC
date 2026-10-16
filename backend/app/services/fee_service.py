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
        student_id: Optional[str] = None,
    ) -> FeePayment:
        """Record an approved payment towards an invoice after verifying ownership and balance."""
        # 1. Fetch invoice details including enrollment student ownership
        inv = self.repo.get_invoice(invoice_id)
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice '{invoice_id}' not found",
            )

        # 2. Verify ownership: student can only pay their own invoice
        if student_id and inv.get("user_id") != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not have permission to pay another student's invoice.",
            )

        # 3. Validate payment amount
        if amount_paid <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment amount must be greater than zero.",
            )

        total_amount = float(inv["amount"])
        already_paid = float(inv.get("amount_paid", 0.0))
        outstanding = round(total_amount - already_paid, 2)

        if outstanding <= 0 or inv.get("status") == "paid":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice is already fully paid.",
            )

        if round(amount_paid, 2) > outstanding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment amount (₹{amount_paid:,.2f}) exceeds outstanding balance of ₹{outstanding:,.2f}.",
            )

        # 4. Atomic transaction update
        payment = self.repo.record_fee_payment(
            invoice_id=invoice_id,
            amount_paid=amount_paid,
            payment_method=payment_method,
            student_id=student_id,
        )
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment could not be processed due to concurrent update or invalid balance.",
            )
        return payment


fee_service = FeeService()
