from fastapi import HTTPException, status



class DatabaseOperationException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed. Please try again later."
        )

class OTPAlreadySentException(HTTPException):
    def __init__(self, wait_seconds: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"OTP already sent. Please wait {wait_seconds // 60}m {wait_seconds % 60}s."
        )

class OTPDeliveryFailedException(HTTPException):
    def __init__(self, reason: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deliver OTP: {reason}"
        )
class InvalidOTPException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )