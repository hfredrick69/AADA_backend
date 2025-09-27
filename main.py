import os
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app

print("🚀 Starting FastAPI application...")

# 1) Load .env
load_dotenv()

# 2) Initialize Firebase Admin from env or file
firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS")
firebase_credentials_file = "/app/firebase_service_key.json"

if firebase_credentials_path and Path(firebase_credentials_path).exists():
    # Standard local dev behavior
    print(f"✅ Using Firebase credentials from local file: {firebase_credentials_path}")
    cred = credentials.Certificate(firebase_credentials_path)
    initialize_app(cred)
elif os.getenv("FIREBASE_CREDENTIALS_JSON"):
    # Azure: write FIREBASE_CREDENTIALS_JSON to file
    print("✅ Writing Firebase credentials from environment to file...")
    try:
        firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        with open(firebase_credentials_file, "w") as f:
            f.write(firebase_credentials_json)
        cred = credentials.Certificate(firebase_credentials_file)
        initialize_app(cred)
        print("✅ Firebase initialized from FIREBASE_CREDENTIALS_JSON.")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to initialize Firebase from env: {e}")
else:
    raise RuntimeError("❌ Firebase credentials not found in path or env.")

# 3) Create FastAPI
app = FastAPI(
    title="AADA Backend API",
    version="1.0",
    description="All AADA endpoints: auth, students, payments, externships, fcm",
    redirect_slashes=False  # 🔥 Prevents auto-redirects like 307
)

# 4) Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5) Import & include your routers
from routers.auth        import router as auth_router
from routers.students    import router as students_router
from routers.payments    import router as payments_router
from routers.externships import router as externships_router
from routers.fcm         import router as fcm_router

app.include_router(auth_router,        prefix="/auth",        tags=["Authentication"])
app.include_router(students_router,    prefix="/students",    tags=["Students"])
app.include_router(payments_router,    prefix="/payments",    tags=["Payments"])
app.include_router(externships_router, prefix="/externships", tags=["Externships"])
app.include_router(fcm_router,         prefix="/fcm",         tags=["FCM"])

# 6) Root health-check
@app.get("/", tags=["Health"])
def read_root():
    return {"message": "✅ AADA Backend API is up and running"}

# 7) (Optional) trigger background tasks on startup
# from routers.database import get_db
# from reminder_task import daily_payment_reminder
#
# @app.on_event("startup")
# async def run_daily_reminder():
#     db = next(get_db())
#     daily_payment_reminder(db)
