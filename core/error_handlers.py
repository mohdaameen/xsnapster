from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
import traceback
import logging

# Import your custom exceptions
from core.exceptions import (
    OTPAlreadySentException,
    OTPDeliveryFailedException,
    InvalidOTPException,
    DatabaseOperationException
)

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI):
    # --- handle specific OTP exceptions first ---
    @app.exception_handler(OTPAlreadySentException)
    async def otp_already_sent_handler(request: Request, exc: OTPAlreadySentException):
        logger.info(f"OTPAlreadySentException on {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": "OTP_ALREADY_SENT",
                "message": exc.detail,
            },
        )

    @app.exception_handler(OTPDeliveryFailedException)
    async def otp_delivery_failed_handler(request: Request, exc: OTPDeliveryFailedException):
        logger.error(f"OTPDeliveryFailedException on {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": "OTP_DELIVERY_FAILED",
                "message": exc.detail,
            },
        )

    @app.exception_handler(InvalidOTPException)
    async def invalid_otp_handler(request: Request, exc: InvalidOTPException):
        logger.warning(f"InvalidOTPException on {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": "INVALID_OTP",
                "message": exc.detail,
            },
        )
    
    @app.exception_handler(DatabaseOperationException)
    async def database_operation_exception_handler(request: Request, exc: DatabaseOperationException):
        logger.error(f"DatabaseOperationException on {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": "DATABASE_OPERATION_FAILED",
                "message": exc.detail,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTPException on {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": "HTTP_EXCEPTION",
                "message": exc.detail,
            },
        )

    # --- handle any uncaught errors ---
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled error on {request.url.path}: {exc}\n{traceback.format_exc()}"
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
            },
        )
