from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session
from db.session import get_db
from services.auth_service import request_otp, verify_otp_and_issue_tokens, refresh_tokens
from schemas.auth import RequestOTP, OTPVerifyRequest, AuthResponse

router = APIRouter(prefix="/v1/auth", tags=["Auth"])

# 1️⃣ Request OTP
@router.post("/request-otp")
def request_otp_route(payload: RequestOTP, db: Session = Depends(get_db)):
    return request_otp(db, payload.identifier)


# 2️⃣ Verify OTP & login (issue tokens)
@router.post("/verify-otp", response_model=AuthResponse)
def verify_otp_route(payload: OTPVerifyRequest, response: Response, db: Session = Depends(get_db)):
    access_token, refresh_token, user = verify_otp_and_issue_tokens(db, payload.identifier, payload.otp)

    # Set refresh token in HttpOnly cookie
    print("Setting refresh token cookie", refresh_token)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "phone_number": user.phone_number,
        },
    }


# 3️⃣ Refresh tokens
@router.post("/refresh", response_model=AuthResponse)
def refresh_token_route(request: Request, response: Response, db: Session = Depends(get_db)):
    access_token, refresh_token, user = refresh_tokens(request, db)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "phone_number": user.phone_number,
        },
    }
