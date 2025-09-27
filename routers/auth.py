# auth.py

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from database import SessionLocal  # adjust if your DB module is named differently
from models import Student

router = APIRouter(
    tags=["Auth"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/login")
def login(
    email: str = Query(..., description="The student's email address"),
    db: Session = Depends(get_db),
):
    """
    Log in a student by email.
    Returns id, name, email, and enrollment_status.
    """
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "enrollment_status": student.enrollment_status,
    }
