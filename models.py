from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, ForeignKey
from datetime import datetime, date
from database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    fcm_token = Column(Text, nullable=True)
    square_customer_id = Column(String, nullable=True)
    # Current enrollment status: Enrolling, Enrolled, Suspended, or Graduated
    enrollment_status = Column(String(30), nullable=False, default="Enrolling")

class PaymentPlan(Base):
    __tablename__ = "payment_plans"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    square_customer_id = Column(String, nullable=True)  # ← Add this line

class PaymentReminderStatus(Base):
    __tablename__ = "payment_reminders"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    reminder_sent = Column(Boolean, default=False, nullable=False)
    overdue_reminder_sent = Column(Boolean, default=False, nullable=False)
    last_checked = Column(Date, default=date.today)

class ExternshipStatus(Base):
    __tablename__ = "externship_status"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    status = Column(String(30), nullable=False)

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    due_date = Column(Date, nullable=False)
    amount_cents = Column(Integer, nullable=False)
    description = Column(Text, default="Monthly Tuition Payment", nullable=False)
    status = Column(String(20), default="PENDING", nullable=False)
    square_invoice_id = Column(String(64), nullable=True)
    reminder_sent = Column(Boolean, default=False, nullable=False)
    late_notice_sent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
