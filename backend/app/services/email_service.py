"""Email delivery service using SMTP."""

import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import get_settings

logger = logging.getLogger(__name__)


async def send_summary_email(recipient: str, summary: str, filename: str) -> None:
    """Send the AI-generated summary via SMTP."""
    settings = get_settings()

    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        raise RuntimeError("SMTP credentials are not configured.")

    html_content = _markdown_to_html(summary, filename)

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USERNAME}>"
    msg["To"] = recipient
    msg["Subject"] = f"Sales Insight Brief \u2013 {filename}"

    msg.attach(MIMEText(summary, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )

    logger.info("Summary email sent to %s via SMTP", recipient)


def _markdown_to_html(summary: str, filename: str) -> str:
    """Convert markdown summary to a styled HTML email."""
    # Escape HTML entities to prevent injection
    import html
    escaped = html.escape(summary)

    # Basic markdown-to-HTML: bold, headers, lists
    lines = escaped.split("\n")
    html_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("### "):
            html_lines.append(f"<h3 style='color:#1a73e8;'>{stripped[4:]}</h3>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2 style='color:#1a73e8;'>{stripped[3:]}</h2>")
        elif stripped.startswith("# "):
            html_lines.append(f"<h1 style='color:#1a73e8;'>{stripped[2:]}</h1>")
        elif stripped.startswith("- "):
            html_lines.append(f"<li>{stripped[2:]}</li>")
        elif stripped.startswith("**") and stripped.endswith("**"):
            html_lines.append(f"<p><strong>{stripped[2:-2]}</strong></p>")
        elif stripped:
            # Handle inline bold
            import re
            processed = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
            html_lines.append(f"<p>{processed}</p>")
        else:
            html_lines.append("<br/>")

    body = "\n".join(html_lines)

    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; color: #333;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 24px; border-radius: 12px 12px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 22px;">📊 Sales Insight Brief</h1>
            <p style="color: rgba(255,255,255,0.85); margin: 8px 0 0;">Generated from: {html.escape(filename)}</p>
        </div>
        <div style="background: #fff; padding: 24px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 12px 12px;">
            {body}
        </div>
        <p style="text-align: center; color: #999; font-size: 12px; margin-top: 16px;">
            Powered by Rabbitt AI Sales Insight Automator
        </p>
    </body>
    </html>
    """
