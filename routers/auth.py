import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from models import User, UserProfile, Student, VerificationToken
from auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_current_active_user
)

router = APIRouter(tags=["Authentication"])

# Pydantic models for request/response
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "student"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class EmailVerificationRequest(BaseModel):
    token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

def generate_verification_token() -> str:
    """Generate a secure random token for email verification."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

@router.post("/register", response_model=dict)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user with email verification."""

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.flush()  # Get the user ID without committing

    # Create user profile
    profile = UserProfile(
        user_id=user.id,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    db.add(profile)

    # Generate email verification token
    verification_token = generate_verification_token()
    token_record = VerificationToken(
        user_id=user.id,
        token=verification_token,
        token_type="email_verification",
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(token_record)

    db.commit()

    # TODO: Send verification email here
    # send_verification_email(user.email, verification_token)

    return {
        "message": "User registered successfully. Please check your email for verification.",
        "user_id": user.id,
        "verification_required": True
    }

@router.post("/login", response_model=TokenResponse)
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens."""

    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )

    # Get user profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    # Create tokens
    access_token = create_access_token(data={"user_id": user.id, "email": user.email})
    refresh_token = create_refresh_token(data={"user_id": user.id})

    # Return user data
    user_data = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "is_verified": user.is_verified,
        "first_name": profile.first_name if profile else None,
        "last_name": profile.last_name if profile else None
    }

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_data
    )

@router.post("/refresh", response_model=dict)
def refresh_access_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""

    try:
        payload = verify_token(request.refresh_token, expected_type="refresh")
        user_id = payload.get("user_id")

        # Verify user still exists and is active
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new access token
        access_token = create_access_token(data={"user_id": user.id, "email": user.email})

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/verify-email")
def verify_email(request: EmailVerificationRequest, db: Session = Depends(get_db)):
    """Verify user email using verification token."""

    # Find the token
    token_record = db.query(VerificationToken).filter(
        VerificationToken.token == request.token,
        VerificationToken.token_type == "email_verification",
        VerificationToken.used == False,
        VerificationToken.expires_at > datetime.utcnow()
    ).first()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    # Mark user as verified
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if user:
        user.is_verified = True
        token_record.used = True
        db.commit()

        return {"message": "Email verified successfully"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

@router.post("/forgot-password")
def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset."""

    user = db.query(User).filter(User.email == request.email).first()
    if user:
        # Generate reset token
        reset_token = generate_verification_token()
        token_record = VerificationToken(
            user_id=user.id,
            token=reset_token,
            token_type="password_reset",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(token_record)
        db.commit()

        # TODO: Send reset email
        # send_password_reset_email(user.email, reset_token)

    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/reset-password")
def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password using reset token."""

    # Find the token
    token_record = db.query(VerificationToken).filter(
        VerificationToken.token == request.token,
        VerificationToken.token_type == "password_reset",
        VerificationToken.used == False,
        VerificationToken.expires_at > datetime.utcnow()
    ).first()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Update password
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if user:
        user.password_hash = get_password_hash(request.new_password)
        token_record.used = True
        db.commit()

        return {"message": "Password reset successfully"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get current user information."""

    # Get user profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_verified": current_user.is_verified,
        "first_name": profile.first_name if profile else None,
        "last_name": profile.last_name if profile else None,
        "phone": profile.phone if profile else None,
        "created_at": current_user.created_at
    }

# Legacy endpoint for backward compatibility
@router.get("/login")
def legacy_login(
    email: str = Query(..., description="The student's email address"),
    db: Session = Depends(get_db),
):
    """
    Legacy login endpoint for backward compatibility.
    Returns student info by email lookup only.
    """
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "enrollment_status": student.enrollment_status,
    }
