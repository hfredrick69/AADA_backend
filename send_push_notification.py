
import firebase_admin
from firebase_admin import credentials, messaging

# Load service account key
cred = credentials.Certificate("firebase_service_key.json")
firebase_admin.initialize_app(cred)

# Replace this with your real device token
fcm_token = "cO2dn-OpIE4Pvwu1ZkgziP:APA91bFHIwRNzyoc_mqjHoV_05yd-o1org9mrrjsyEHCAlbUNPvlWHVbK0pFkrYpas-FCDR-K0ZYNf4Ez3Du8elG8mLr9XjcAHJEocXbGepPYruVhL_bnz0"

# Build and send the message
message = messaging.Message(
    notification=messaging.Notification(
        title="Payment Reminder",
        body="Your payment is due in 3 days!"
    ),
    token=fcm_token,
)

# Send the message
response = messaging.send(message)
print("✅ Successfully sent message:", response)
