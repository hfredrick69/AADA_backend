from database import SessionLocal
from models import Student, PaymentPlan, ExternshipStatus
from datetime import date

db = SessionLocal()

# Check if student exists
student = db.query(Student).filter_by(email="jane@example.com").first()

if not student:
    student = Student(name="Jane Doe", email="jane@example.com")
    db.add(student)
    db.commit()
    db.refresh(student)

# Add test payments (some future, some past)
payments = [
    PaymentPlan(student_id=student.id, amount=500, due_date=date(2025, 7, 1)),
    PaymentPlan(student_id=student.id, amount=400, due_date=date(2024, 6, 1)),
    PaymentPlan(student_id=student.id, amount=600, due_date=date(2025, 8, 1))
]

db.add_all(payments)
db.commit()
db.close()
