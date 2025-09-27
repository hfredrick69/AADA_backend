# reminder_task.py

import os
import requests
from datetime import date, timedelta

from firebase_admin.messaging import Message, send
from sqlalchemy.orm import Session

from models import Invoice, Student

# ────────────────────────────────────────────────────────────────────────────────
# Configuration: read your Square credentials + version from env
# ────────────────────────────────────────────────────────────────────────────────
SQUARE_TOKEN = os.getenv("SQUARE_ACCESS_TOKEN")
if not SQUARE_TOKEN:
    raise RuntimeError("Missing SQUARE_ACCESS_TOKEN in environment")

# Decide base URL based on environment
env = os.getenv("SQUARE_ENVIRONMENT", "sandbox").lower()
if env == "production":
    SQUARE_BASE = "https://connect.squareup.com"
else:
    SQUARE_BASE = "https://connect.squareupsandbox.com"

# Square API version header
SQUARE_VERSION = os.getenv("SQUARE_API_VERSION", "2024-06-12")

HEADERS = {
    "Authorization": f"Bearer {SQUARE_TOKEN}",
    "Square-Version": SQUARE_VERSION,
    "Content-Type": "application/json"
}


def check_invoice_paid(invoice_id: str) -> bool:
    """
    Fetch the invoice from Square and return True if its status is PAID.
    """
    url = f"{SQUARE_BASE}/v2/invoices/{invoice_id}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json().get("invoice", {})
    return data.get("status", "").upper() == "PAID"


def _send_push(student: Student, title: str, body: str):
    """Helper to send an FCM message to a student."""
    if not student.fcm_token:
        print(f"⚠️ No FCM token for {student.id}")
        return

    message = Message(
        token=student.fcm_token,
        notification={"title": title, "body": body}
    )
    try:
        send(message)
        print(f"✅ Sent '{title}' to {student.email}")
    except Exception as e:
        print(f"❌ Failed to send push to {student.email}: {e}")


def daily_payment_reminder(db: Session):
    """Run once a day:
       - Remind 3 days before due_date
       - Notify 2 days after overdue
       - Sync PAID status from Square
    """
    today = date.today()
    upcoming_cutoff = today + timedelta(days=3)
    late_cutoff = today - timedelta(days=2)

    # Fetch all invoices that have a Square ID
    invoices = (
        db.query(Invoice)
          .filter(Invoice.square_invoice_id.isnot(None))
          .all()
    )

    for inv in invoices:
        student = db.query(Student).filter_by(id=inv.student_id).first()
        if not student:
            continue

        # 1) Sync status from Square
        try:
            paid = check_invoice_paid(inv.square_invoice_id)
        except Exception as e:
            print(f"⚠️ Could not check {inv.square_invoice_id}: {e}")
            paid = False

        if paid and inv.status != "PAID":
            inv.status = "PAID"
            db.commit()
            _send_push(
                student,
                "Payment Received",
                f"Thanks, we received your payment for ${inv.amount_cents/100:.2f}."
            )

        # 2) Upcoming reminder (3 days before)
        if inv.status != "PAID" and not inv.reminder_sent and inv.due_date == upcoming_cutoff:
            _send_push(
                student,
                "Payment Due Soon",
                f"Your payment of ${inv.amount_cents/100:.2f} is due on {inv.due_date}."
            )
            inv.reminder_sent = True
            db.commit()

        # 3) Late notice (2 days after)
        if inv.status != "PAID" and not inv.late_notice_sent and inv.due_date <= late_cutoff:
            _send_push(
                student,
                "Payment Overdue",
                f"Your payment of ${inv.amount_cents/100:.2f} was due on {inv.due_date}."
            )
            inv.late_notice_sent = True
            db.commit()
