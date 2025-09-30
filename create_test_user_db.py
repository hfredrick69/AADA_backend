#!/usr/bin/env python3
"""
Create a test user directly in the AADA database
"""
import sys
import psycopg2
from passlib.context import CryptContext
from datetime import datetime

# Database connection from .env
DATABASE_URL = "postgresql://aadaadmin:Universe1111@aada-pg-server27841.postgres.database.azure.com:5432/aada_local?sslmode=require"

# Password hashing (same as backend)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test user credentials
TEST_EMAIL = "webtest@aada.edu"
TEST_PASSWORD = "WebTest123!"
TEST_FIRST_NAME = "Web"
TEST_LAST_NAME = "Tester"
TEST_PHONE = "4045551234"

def create_test_user():
    """Create a test user in the database"""
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT id, email FROM users WHERE email = %s", (TEST_EMAIL,))
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"\n⚠️  User already exists: {existing_user[1]} (ID: {existing_user[0]})")
            print("Updating password instead...")

            # Update password
            hashed_password = pwd_context.hash(TEST_PASSWORD)
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE email = %s",
                (hashed_password, TEST_EMAIL)
            )
            conn.commit()
            user_id = existing_user[0]
            print("✅ Password updated successfully!")

        else:
            print("Creating new user...")

            # Hash the password
            hashed_password = pwd_context.hash(TEST_PASSWORD)

            # Insert user
            now = datetime.utcnow()
            cursor.execute("""
                INSERT INTO users (email, password_hash, role, is_active, is_verified, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (TEST_EMAIL, hashed_password, 'student', True, True, now, now))

            user_id = cursor.fetchone()[0]
            print(f"✅ User created with ID: {user_id}")

            # Insert user profile
            cursor.execute("""
                INSERT INTO user_profiles (user_id, first_name, last_name, phone, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, TEST_FIRST_NAME, TEST_LAST_NAME, TEST_PHONE, now, now))

            print("✅ User profile created")

            # Commit transaction
            conn.commit()

        # Display credentials
        print("\n" + "=" * 60)
        print("TEST USER CREDENTIALS")
        print("=" * 60)
        print(f"Email:    {TEST_EMAIL}")
        print(f"Password: {TEST_PASSWORD}")
        print(f"Name:     {TEST_FIRST_NAME} {TEST_LAST_NAME}")
        print(f"Phone:    {TEST_PHONE}")
        print("=" * 60)
        print("\n✅ You can now login at: http://localhost:5173")

        # Close connection
        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_test_user()