#!/usr/bin/env python3
import os
import sys
from datetime import datetime, timedelta

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Student, PaymentPlan
import httpx

load_dotenv()

# 1) Determine Square API base URL based on environment
ENV = os.getenv("SQUARE_ENVIRONMENT", "production").lower()
if ENV == "sandbox":
    SQUARE_API_BASE = "https://connect.squareupsandbox.com/v2"
else:
    SQUARE_API_BASE = "https://connect.squareup.com/v2"

# 2) API version header
SQUARE_API_VERSION = "2024-06-12"

def get_headers():
    token = os.getenv("SQUARE_ACCESS_TOKEN")
    if not token:
        print("❌ Missing SQUARE_ACCESS_TOKEN environment variable")
        sys.exit(1)
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Square-Version": SQUARE_API_VERSION,
    }

def create_order(customer_id: str, amount: int, student_name: str) -> str:
    """
    Create a draft order in Square for the given customer_id and amount (in cents).
    Returns the order_id.
    """
    location_id = os.getenv("SQUARE_LOCATION_ID")
    if not location_id:
        print("❌ Missing SQUARE_LOCATION_ID environment variable")
        sys.exit(1)

    url = f"{SQUARE_API_BASE}/orders"
    payload = {
      "order": {
        "location_id": location_id,
        "customer_id": customer_id,
        "line_items": [
          {
            "name": f"Tuition Invoice for {student_name}",
            "quantity": "1",
            "base_price_money": {
              "amount": amount,
              "currency": "USD"
            }
          }
        ]
      }
    }
    resp = httpx.post(url, json=payload, headers=get_headers(), timeout=10)
    if resp.status_code in (200, 201):
        data = resp.json().get("order", {})
        return data["id"]
    else:
        print("❌ Order creation failed:", resp.json())
        sys.exit(1)

def create_invoice(customer_id: str, amount: int, due_date: str, student_name: str):
    """
    Create an invoice in Square for the given customer_id, amount and due_date.
    Uses a BALANCE payment_request with no fixed_amount_requested_money.
    """
    location_id = os.getenv("SQUARE_LOCATION_ID")
    if not location_id:
        print("❌ Missing SQUARE_LOCATION_ID environment variable")
        sys.exit(1)

    order_id = create_order(customer_id, amount, student_name)
    url = f"{SQUARE_API_BASE}/invoices"
    payload = {
        "invoice": {
            "location_id": location_id,
            "order_id": order_id,
            "primary_recipient": {"customer_id": customer_id},
            "payment_requests": [
                {
                    "request_type": "BALANCE",
                    "due_date": due_date
                }
            ],
            "delivery_method": "EMAIL",
            "accepted_payment_methods": {
                "card": True,
                "square_gift_card": False,
                "bank_account": False,
                "buy_now_pay_later": False,
                "cash_app_pay": False
            },
            "invoice_number": f"{student_name}-{due_date}"
        }
    }
    resp = httpx.post(url, json=payload, headers=get_headers(), timeout=10)
    if resp.status_code in (200, 201):
        print(f"✅ Invoice created for {student_name} due {due_date}")
    else:
        print("❌ Invoice creation failed:", resp.json())

def main(student_id: int):
    db: Session = SessionLocal()
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        print(f"❌ No student found with id {student_id}")
        return

    plan = db.query(PaymentPlan).filter_by(student_id=student_id).first()
    if not plan:
        print(f"❌ No payment plan for {student.name}")
        return

    today = datetime.today()
    # Generate four invoices, two weeks apart starting today
    for i in range(4):
        due = (today + timedelta(weeks=2 * i)).strftime("%Y-%m-%d")
        create_invoice(plan.square_customer_id, plan.amount, due, student.name)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_test_invoices.py <student_id>")
        sys.exit(1)
    try:
        sid = int(sys.argv[1])
    except ValueError:
        print("❌ student_id must be an integer")
        sys.exit(1)
    main(sid)
