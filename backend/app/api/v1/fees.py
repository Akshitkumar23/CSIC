"""Student fee billing, ledger, and transaction payment endpoints."""
from fastapi import APIRouter, Depends, Query

from backend.app.core.security import (
    get_current_user,
    require_student,
    verify_student_access,
)
from backend.app.models.auth import UserProfile
from backend.app.models.fee import FeePayment, FeeSummary
from backend.app.services.fee_service import fee_service

router = APIRouter(prefix="/fees", tags=["Fees & Invoices"])


@router.get("/me", response_model=FeeSummary, summary="Get current student fee ledger")
async def get_my_fee_summary(
    current_user: UserProfile = Depends(require_student),
) -> FeeSummary:
    """Fetch all semester fee invoices, payment receipts, and outstanding dues."""
    return fee_service.get_summary(current_user.id)


@router.get("/student/{student_id}", response_model=FeeSummary, summary="Get student fee ledger by ID")
async def get_student_fee_summary(
    student_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> FeeSummary:
    """Fetch fee invoices and outstanding balance for a specified student."""
    verify_student_access(current_user, student_id)
    return fee_service.get_summary(student_id)


@router.post(
    "/invoices/{invoice_id}/pay",
    response_model=FeePayment,
    summary="Make payment towards an invoice",
)
async def pay_invoice(
    invoice_id: str,
    amount: float = Query(..., gt=0.0, description="Amount to be paid in INR"),
    payment_method: str = Query("upi", description="Payment method: upi, card, net_banking"),
    current_user: UserProfile = Depends(require_student),
) -> FeePayment:
    """Simulate instantaneous settlement of an institutional tuition fee invoice."""
    return fee_service.process_payment(
        invoice_id=invoice_id,
        amount_paid=amount,
        payment_method=payment_method,
        student_id=current_user.id,
    )
