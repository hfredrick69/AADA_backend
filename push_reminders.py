#!/usr/bin/env python3
"""
Script: push_reminders.py

Daily job to send payment reminders via FCM:
- "Payment Reminder" 3 days before due.
- "Payment Late" 2+ days after due.

Uses:
  students(id, fcm_token)
  invoices(id, student_id, due_date, amount_cents, reminder_sent, late_notice_sent)

Helper:
  fcm_reminder.send_push_notification(token, message)
"""
import os
from datetime import date

from database import SessionLocal
from models import Student, Invoice
from fcm_reminder import send_push_notification as send_push


def run_reminders():
    session = SessionLocal()
    today = date.today()

    # Process all invoices
    invoices = session.query(Invoice).all()
    for inv in invoices:
        # Debug invoice state
        delta = (inv.due_date - today).days
        print(f"[DEBUG] Invoice {inv.id}: due={inv.due_date}, delta={delta}, reminder_sent={inv.reminder_sent}, late_notice_sent={inv.late_notice_sent}")

        student = session.get(Student, inv.student_id)
        if not student or not student.fcm_token:
            print(f"[DEBUG] Skipping invoice {inv.id}: missing student or token")
            continue

        # Reminder: 3 days before due_date
        if delta == 3 and not inv.reminder_sent:
            message = f"Your payment of ${inv.amount_cents/100:.2f} is due on {inv.due_date:%Y-%m-%d}."
            send_push(student.fcm_token, message)
            inv.reminder_sent = True
            inv.updated_at = today
            print(f"✅ Reminder sent to {student.name} for invoice due {inv.due_date}")

        # Late notice: 2 or more days after due_date
        elif delta <= -2 and not inv.late_notice_sent:
            message = f"Your payment of ${inv.amount_cents/100:.2f} was due on {inv.due_date:%Y-%m-%d}. Please pay ASAP."
            send_push(student.fcm_token, message)
            inv.late_notice_sent = True
            inv.updated_at = today
            print(f"✅ Late notice sent to {student.name} for invoice due {inv.due_date}")

        else:
            print(f"[DEBUG] No action for invoice {inv.id} (delta={delta})")

    session.commit()
    session.close()


if __name__ == '__main__':
    run_reminders()
