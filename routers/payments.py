# routers/payments.py

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import PaymentPlan

router = APIRouter(
    tags=["Payments"],
)

@router.get("", include_in_schema=False)
@router.get("/", summary="Get payment plans for a student")
def get_payments(
    student_id: int = Query(..., description="ID of the student"),
    db: Session = Depends(get_db),
) -> List[dict]:
    """
    Returns all payment plans (amount + due_date) for the given student_id,
    ordered by due_date. If none exist, returns [].
    """
    plans = (
        db.query(PaymentPlan)
        .filter(PaymentPlan.student_id == student_id)
        .order_by(PaymentPlan.due_date)
        .all()
    )

    return [
        {
            "student_id": p.student_id,
            "amount": p.amount,
            "due_date": p.due_date.isoformat()
        }
        for p in plans
    ]
