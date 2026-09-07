"""Label normalization shared by the factor catalog and the spatial allocator.

Korean source labels are preserved; only the derived code label is folded to a
stable form so that CAPSS categories join reliably across workbooks.
"""

from __future__ import annotations

import re
import unicodedata

import pandas as pd


def clean_cell(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = unicodedata.normalize("NFKC", str(value))
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def normalize_label(value: object) -> str | None:
    """Create a stable ASCII-ish code label while retaining Korean source labels."""
    text = clean_cell(value)
    if text is None:
        return None
    text = text.lower()
    text = re.sub(r"[^0-9a-z가-힣]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or None
