# routers/externships.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ExternshipStatus

router = APIRouter(tags=["Externships"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "",  # No trailing slash; root of the /externships prefix
    summary="Get externship status for a student",
    response_model=dict,
    response_description="Externship status object for the given student"
)
def get_externship_status(
    student_id: int = Query(..., description="ID of the student"),
    db: Session = Depends(get_db),
):
    """
    Returns the current externship status for the given student.
    If no record exists, returns: {"student_id": ..., "status": "Not Started"}
    """
    record = (
        db.query(ExternshipStatus)
        .filter(ExternshipStatus.student_id == student_id)
        .first()
    )

    if not record:
        return {"student_id": student_id, "status": "Not Started"}

    return {"student_id": student_id, "status": record.status}
