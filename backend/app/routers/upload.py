"""Upload router – handles file upload, AI summarization, and email delivery."""

import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.services.data_parser import parse_upload
from app.services.ai_engine import generate_summary
from app.services.email_service import send_summary_email

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Sales Insights"])

limiter = Limiter(key_func=get_remote_address)


class UploadResponse(BaseModel):
    """Response model for the upload endpoint."""

    success: bool
    message: str
    summary: str | None = None
    rows_processed: int | None = None


class HealthResponse(BaseModel):
    """Response model for the health check."""

    status: str
    version: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns the health status and version of the API.",
)
async def health_check():
    settings = get_settings()
    return HealthResponse(status="healthy", version=settings.APP_VERSION)


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload Sales Data",
    description=(
        "Upload a `.csv` or `.xlsx` file along with a recipient email address. "
        "The system will parse the data, generate an AI-powered executive summary, "
        "and email the brief to the specified address."
    ),
    responses={
        200: {"description": "Summary generated and emailed successfully."},
        400: {"description": "Invalid file format or data."},
        413: {"description": "File too large."},
        429: {"description": "Rate limit exceeded."},
        500: {"description": "Internal server error during processing."},
    },
)
@limiter.limit("10/minute")
async def upload_and_summarize(
    request: Request,
    file: UploadFile = File(
        ..., description="Sales data file (.csv or .xlsx, max 10 MB)"
    ),
    email: str = Form(
        ..., description="Recipient email address for the summary brief"
    ),
):
    settings = get_settings()

    # --- Validate email ---
    try:
        EmailStr._validate(email)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid email address.")

    # --- Validate file size ---
    content = await file.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {settings.MAX_FILE_SIZE_MB} MB limit.",
        )
    # Reset file position after reading
    await file.seek(0)

    # --- Step 1: Parse the data ---
    try:
        data_summary = await parse_upload(file)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Data parsing failed")
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")

    # --- Step 2: Generate AI summary ---
    try:
        summary_text = await generate_summary(data_summary)
    except RuntimeError as e:
        logger.exception("AI generation failed")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("AI generation failed unexpectedly")
        raise HTTPException(
            status_code=500, detail="Failed to generate AI summary."
        )

    # --- Step 3: Send email ---
    try:
        await send_summary_email(email, summary_text, file.filename or "data")
    except RuntimeError as e:
        logger.exception("Email sending failed")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Email sending failed unexpectedly")
        raise HTTPException(
            status_code=500, detail="Failed to send email. Summary was generated but delivery failed."
        )

    return UploadResponse(
        success=True,
        message=f"Sales brief generated and sent to {email}.",
        summary=summary_text,
        rows_processed=data_summary.get("total_rows", 0),
    )
