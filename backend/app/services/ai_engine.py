"""AI engine service – generates narrative summaries from parsed sales data via Groq API."""

import json
import httpx
from app.config import get_settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are a senior business analyst at Rabbitt AI. Your job is to take raw sales data and produce a polished, executive-ready narrative summary.

Your summary MUST include:
1. **Executive Overview** – A 2-3 sentence high-level summary of the quarter's performance.
2. **Key Metrics** – Total revenue, units sold, average deal size, and any standout numbers.
3. **Regional Performance** – How different regions performed relative to each other.
4. **Product Insights** – Which product categories drove the most revenue/volume.
5. **Trends & Observations** – Any notable patterns in timing, growth, or anomalies.
6. **Actionable Recommendations** – 2-3 concrete suggestions for the next quarter.

Format the output in clean Markdown. Be concise, data-driven, and professional.
Do NOT fabricate data points that aren't in the source. If data is insufficient, state so."""


async def generate_summary(data_summary: dict) -> str:
    """Generate an AI narrative summary from parsed data using the Groq API."""
    settings = get_settings()

    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    user_prompt = _build_user_prompt(data_summary)

    payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2048,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    if resp.status_code != 200:
        error_detail = resp.json().get("error", {}).get("message", resp.text)
        raise RuntimeError(f"Groq API error ({resp.status_code}): {error_detail}")

    data = resp.json()
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError("AI model returned an unexpected response format.")

    if not text:
        raise RuntimeError("AI model returned an empty response.")

    return text


def _build_user_prompt(data_summary: dict) -> str:
    """Build a structured prompt from the data summary."""
    parts = [
        f"## Sales Data File: {data_summary.get('filename', 'Unknown')}",
        f"**Total Records:** {data_summary.get('total_rows', 'N/A')}",
        f"**Columns:** {', '.join(data_summary.get('columns', []))}",
    ]

    if "total_revenue" in data_summary:
        parts.append(f"**Total Revenue:** ${data_summary['total_revenue']:,.2f}")

    if "statistics" in data_summary:
        parts.append("\n### Statistical Summary")
        parts.append("```json")
        parts.append(json.dumps(data_summary["statistics"], indent=2, default=str))
        parts.append("```")

    if "category_breakdowns" in data_summary:
        parts.append("\n### Category Breakdowns")
        for cat, values in data_summary["category_breakdowns"].items():
            parts.append(f"\n**{cat}:**")
            for k, v in values.items():
                parts.append(f"  - {k}: {v}")

    parts.append("\n### Raw Data Preview (first 50 rows)")
    parts.append("```csv")
    parts.append(data_summary.get("raw_preview", "No preview available"))
    parts.append("```")

    parts.append("\nPlease generate a comprehensive executive sales brief from this data.")

    return "\n".join(parts)
