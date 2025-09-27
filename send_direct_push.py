
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Load credentials
creds = service_account.Credentials.from_service_account_file(
    'firebase_service_key.json',
    scopes=['https://www.googleapis.com/auth/firebase.messaging'],
)

creds.refresh(Request())
access_token = creds.token

# Replace with your device token
fcm_token = "cO2dn-OpIE4Pvwu1ZkgziP:APA91bFHIwRNzyoc_mqjHoV_05yd-o1org9mrrjsyEHCAlbUNPvlWHVbK0pFkrYpas-FCDR-K0ZYNf4Ez3Du8elG8mLr9XjcAHJEocXbGepPYruVhL_bnz0"

# Build message payload
message = {
    "message": {
        "token": fcm_token,
        "notification": {
            "title": "Payment Reminder",
            "body": "Your payment is due in 3 days!"
        }
    }
}

project_id = creds.project_id
url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

# Send request
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, json=message)

print("Status Code:", response.status_code)
print("Response:", response.text)
