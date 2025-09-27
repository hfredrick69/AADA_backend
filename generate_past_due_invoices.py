import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Student, PaymentPlan
import httpx

load_dotenv()

SQUARE_API_BASE = "https://connect.squareup.com/v2"
SQUARE_API_VERSION = "2024-06-12"

def get_headers():
    token = os.getenv("SQUARE_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("SQUARE_ACCESS_TOKEN must be set.")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Square-Version": SQUARE_API_VERSION,
    }

def create_invoice(customer_id: str, amount_cents: int, due_date: str, student_name: str) -> str | None:
    location_id = os.getenv("SQUARE_LOCATION_ID")
    if not location_id:
        raise RuntimeError("SQUARE_LOCATION_ID must be set.")

    payload = {
        "invoice": {
            "location_id": location_id,
            "primary_recipient": {"customer_id": customer_id},
            "payment_requests": [
                {
                    "request_type": "BALANCE",
                    "due_date": due_date
                }
            ],
            "invoice_number": f"PASTDUE-{datetime.now():%Y%m%d%H%M%S}",
            "title": f"{student_name} Past Due Tuition",
            "description": "Automatically generated past due invoice",
            "delivery_method": "EMAIL",
            "accepted_payment_methods": {
                "card": True,
                "square_gift_card": False,
                "bank_account": False
            },
            "line_items": [
                {
                    "name": "Past Due Tuition",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": amount_cents,
                        "currency": "USD"
                    }
                }
            ]
        }
    }

    try:
        resp = httpx.post(
            f"{SQUARE_API_BASE}/invoices",
            headers=get_headers(),
            json=payload
        )
        if resp.status_code == 200:
            inv_id = resp.json()["invoice"]["id"]
            print(f"✅ Created invoice {inv_id} for {student_name}, due {due_date}")
            return inv_id
        else:
            print("❌ Error:", resp.text)
    except httpx.RequestError as e:
        print("❌ Request Error:", e)
    return None

def get_missed_due_dates(start_date: datetime, today: datetime, interval_days: int):
    due_dates = []
    cursor = start_date
    while cursor < today:
        due_dates.append(cursor)
        cursor += timedelta(days=interval_days)
    return due_dates

def main():
    db: Session = SessionLocal()
    today = datetime.today()
    students = db.query(Student).join(PaymentPlan).all()
    print(f"📦 Found {len(students)} students with payment plans.")

    for student in students:
        plan = db.query(PaymentPlan).filter_by(student_id=student.id).first()
        if not plan or not plan.square_customer_id:
            continue
        for due_dt in get_missed_due_dates(plan.start_date, today, plan.interval_days or 14):
            create_invoice(
                plan.square_customer_id,
                plan.amount_cents,
                due_dt.strftime("%Y-%m-%d"),
                student.full_name
            )

if __name__ == "__main__":
    main()
