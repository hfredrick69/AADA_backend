#!/usr/bin/env python3
"""
Script: update_all_fcm_tokens.py

Copies the FCM token from the student record named "Jane Doe" to every student in the database.
Run this once to unify all fcm_token values.
"""
import os
from database import SessionLocal
from models import Student


def main():
    session = SessionLocal()

    # Find Jane Doe's record
    jane = session.query(Student).filter_by(name="Jane Doe").first()
    if not jane:
        print("Error: No student with name 'Jane Doe' found.")
        session.close()
        return
    if not jane.fcm_token:
        print("Error: 'Jane Doe' has no fcm_token set.")
        session.close()
        return

    token = jane.fcm_token
    print(f"Copying Jane Doe's fcm_token ({token}) to all students...")

    # Update all students
    session.query(Student).update({Student.fcm_token: token})
    session.commit()
    session.close()
    print("✅ All students' fcm_token fields have been updated.")


if __name__ == '__main__':
    main()
