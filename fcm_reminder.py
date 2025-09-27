
import firebase_admin
from firebase_admin import credentials, messaging

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_service_key.json")
    firebase_admin.initialize_app(cred)

def send_push_notification(fcm_token, message):
    notification = messaging.Message(
        notification=messaging.Notification(
            title="AADA Payment Reminder",
            body=message,
        ),
        token=fcm_token
    )
    response = messaging.send(notification)
    print("✅ Push sent:", response)
