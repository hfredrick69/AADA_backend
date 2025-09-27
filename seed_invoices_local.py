#!/usr/bin/env python3
"""
Seed all students’ invoices for the 15th of the current month.
Deletes any existing invoices for that date before inserting.
"""
from datetime import date
from database import SessionLocal
from models import Student, PaymentPlan, Invoice

def seed_current_month():
    session = SessionLocal()
    today = date.today()
    due = today.replace(day=15)

    # Remove any that we already seeded for this month
    session.query(Invoice)\
        .filter(Invoice.due_date == due)\
        .delete(synchronize_session=False)

    # Map each student to their plan amount
    plans = {p.student_id: p.amount for p in session.query(PaymentPlan)}

    for student in session.query(Student):
        amt = plans.get(student.id)
        if amt is None:
            print(f"⚠️  No plan for {student.name} ({student.id}); skipping.")
            continue

        inv = Invoice(
            student_id=student.id,
            due_date=due,
            amount_cents=amt,
            # description defaults to “Monthly Tuition Payment”
        )
        session.add(inv)
        print(f"Seeded invoice for {student.name} due {due} (${amt/100:.2f})")

    session.commit()
    session.close()

if __name__ == "__main__":
    seed_current_month()
