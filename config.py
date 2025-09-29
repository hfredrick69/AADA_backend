"""
Configuration settings for AADA Backend API
Contains secure default keys and environment variable fallbacks
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Secure default keys - generated using secrets.token_urlsafe(32)
# These ensure the app always has valid keys even if environment variables aren't set
DEFAULT_JWT_SECRET_KEY = "b8mwapwQ84qbkpZVEX3xlirwAZCNpCWLS7Hd6P0UbCM"
DEFAULT_SECRET_KEY = "EsMby6XbhBj24Za91_ZQevn1Iuj4nrJP1-ZFISAUp68"

# Configuration class
class Config:
    # Security keys with environment variable fallback to secure defaults
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", DEFAULT_JWT_SECRET_KEY)
    SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)

    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/aada_local")

    # JWT settings
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # Azure Storage
    AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")

    # SendGrid Email
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

    # Firebase
    FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

# Global config instance
config = Config()