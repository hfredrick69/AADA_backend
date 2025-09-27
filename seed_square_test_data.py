import os
from dotenv import load_dotenv
import httpx

load_dotenv()

SQUARE_API_BASE = "https://connect.squareup.com/v2"
SQUARE_API_VERSION = "2024-06-12"  # Adjust as needed

def get_headers():
    token = os.getenv("SQUARE_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("SQUARE_ACCESS_TOKEN must be set.")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Square-Version": SQUARE_API_VERSION,
    }

def create_test_customer(first_name: str, last_name: str, email: str) -> str | None:
    payload = {
        "given_name": first_name,
        "family_name": last_name,
        "email_address": email
    }
    response = httpx.post(f"{SQUARE_API_BASE}/customers", headers=get_headers(), json=payload)

    if response.status_code == 200:
        customer_id = response.json()["customer"]["id"]
        print(f"✅ Created customer: {customer_id}")
        return customer_id
    else:
        print("❌ Failed to create customer")
        print(response.text)
        return None

def create_invoice(customer_id: str, amount_cents: int, due_date: str) -> str | None:
    location_id = os.getenv("SQUARE_LOCATION_ID")
    if not location_id:
        raise RuntimeError("SQUARE_LOCATION_ID must be set.")

    invoice_data = {
        "invoice": {
            "location_id": location_id,
            "primary_recipient": {"customer_id": customer_id},
            "payment_requests": [
                {
                    "request_type": "BALANCE",
                    "due_date": due_date
                }
            ],
            "invoice_number": "TEST-001",
            "title": "Test Invoice",
            "description": "Test invoice for seeding",
            "delivery_method": "EMAIL",
            "accepted_payment_methods": {
                "card": True,
                "square_gift_card": False,
                "bank_account": False
            },
            "line_items": [
                {
                    "name": "Test Dental Service",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": amount_cents,
                        "currency": "USD"
                    }
                }
            ]
        }
    }

    response = httpx.post(f"{SQUARE_API_BASE}/invoices", headers=get_headers(), json=invoice_data)

    if response.status_code == 200:
        invoice_id = response.json()["invoice"]["id"]
        print(f"✅ Created invoice: {invoice_id}")
        return invoice_id
    else:
        print("❌ Failed to create invoice")
        print(response.text)
        return None

def list_locations() -> None:
    response = httpx.get(f"{SQUARE_API_BASE}/locations", headers=get_headers())
    if response.status_code == 200:
        for loc in response.json()["locations"]:
            print(f"📍 Location: {loc['name']} — {loc['id']}")
    else:
        print("❌ Failed to fetch locations")
        print(response.text)

if __name__ == "__main__":
    list_locations()
    cust = create_test_customer("Jane", "Doe", "jane.doe@example.com")
    if cust:
        create_invoice(cust, 5000, "2025-07-10")
