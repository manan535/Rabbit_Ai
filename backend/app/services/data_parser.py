"""Data parsing service for CSV/XLSX files."""

import io
import pandas as pd
from fastapi import UploadFile, HTTPException


ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_ROWS = 50_000


async def parse_upload(file: UploadFile) -> dict:
    """Parse an uploaded CSV or Excel file and return structured data."""
    filename = file.filename or ""
    ext = _get_extension(filename)

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        df = _read_dataframe(content, ext)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to parse file: {str(e)}"
        )

    if len(df) > MAX_ROWS:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum of {MAX_ROWS:,} rows.",
        )

    # Build a summary dict for the AI engine
    summary = _build_data_summary(df)
    summary["filename"] = filename
    summary["raw_preview"] = df.head(50).to_csv(index=False)
    return summary


def _get_extension(filename: str) -> str:
    import os
    return os.path.splitext(filename)[1].lower()


def _read_dataframe(content: bytes, ext: str) -> pd.DataFrame:
    buf = io.BytesIO(content)
    if ext == ".csv":
        return pd.read_csv(buf)
    return pd.read_excel(buf, engine="openpyxl")


def _build_data_summary(df: pd.DataFrame) -> dict:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    summary = {
        "total_rows": len(df),
        "columns": df.columns.tolist(),
        "numeric_columns": numeric_cols,
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }

    # Aggregate stats for numeric columns
    if numeric_cols:
        stats = df[numeric_cols].describe().to_dict()
        summary["statistics"] = stats

    # Category breakdowns for object columns
    cat_cols = df.select_dtypes(include="object").columns.tolist()
    breakdowns = {}
    for col in cat_cols[:5]:  # limit to first 5 categorical columns
        breakdowns[col] = df[col].value_counts().head(10).to_dict()
    summary["category_breakdowns"] = breakdowns

    # If Revenue-like column exists, add totals
    revenue_cols = [c for c in df.columns if "revenue" in c.lower() or "sales" in c.lower()]
    if revenue_cols:
        for col in revenue_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                summary[f"total_{col.lower()}"] = float(df[col].sum())

    return summary
