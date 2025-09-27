# routers/fcm.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Student

router = APIRouter(
    tags=["FCM"],
)

class FCMTokenPayload(BaseModel):
    fcm_token: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/students/{student_id}/fcm-token",
    summary="Register or update a student's FCM token"
)
def register_fcm_token(
    student_id: int,
    payload: FCMTokenPayload,
    db: Session = Depends(get_db),
):
    """
    Persists the FCM token for push notifications for the given student.
    """
    # NOTE: Student.id is the column on your model—not Student.student_id
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.fcm_token = payload.fcm_token
    db.commit()
    return {"message": "FCM token registered"}
