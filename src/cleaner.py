"""Các quy tắc chuẩn hóa dữ liệu bất động sản nhà phố TP.HCM.

Áp dụng cho `real_estate_with_price_per_m2.csv`:
1. `district` — giá trị dạng số "1".."12" → "Quận 1".."Quận 12"; các quận nội thành
   không có prefix → thêm "Quận "; các huyện ngoại thành → thêm "Huyện ".
2. `house_direction` — 12 giá trị bao gồm dạng ghép "Đông - Nam" → chuẩn về 8 hướng
   chính bằng cách bỏ dấu "-" và ghép hai phần (ví dụ "Đông - Nam" → "Đông Nam").
3. `total_price` — bỏ NaN và bỏ giá trị < 100 triệu (chắc chắn sai).
4. `area_m2` — bỏ dòng có diện tích < 5m² hoặc > 1000m² (outlier rõ ràng).
5. `bedrooms` — bỏ dòng có số phòng > 15.
6. `price_per_m2` — tính lại từ `total_price / area_m2` để đảm bảo nhất quán.
"""

from __future__ import annotations

import re
from typing import Optional

import pandas as pd


_NUMBER_TO_QUAN = {str(i): f"Quận {i}" for i in range(1, 13)}

# Các quận nội thành (không có số, không có "Quận"/"Huyện" prefix)
_INNER_QUAN = {
    "Bình Thạnh",
    "Tân Bình",
    "Gò Vấp",
    "Phú Nhuận",
    "Tân Phú",
    "Bình Tân",
}

# Các huyện ngoại thành
_OUTER_HUYEN = {
    "Bình Chánh",
    "Củ Chi",
    "Cần Giờ",
    "Hóc Môn",
    "Nhà Bè",
    "Thủ Đức",
}

# Hướng đã chuẩn (để kiểm tra)
_KNOWN_DIRECTIONS = {
    "Đông", "Tây", "Nam", "Bắc",
    "Đông Nam", "Tây Nam", "Đông Bắc", "Tây Bắc",
}

_DIR_SPLIT_RE = re.compile(r"\s*[-–—]\s*")


def normalize_district(value: Optional[str]) -> Optional[str]:
    """Trả về tên quận/huyện chuẩn. None nếu đầu vào rỗng."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if s in _NUMBER_TO_QUAN:
        return _NUMBER_TO_QUAN[s]
    if s.startswith("Quận ") or s.startswith("Huyện ") or s.startswith("TP. "):
        return s
    if s in _INNER_QUAN:
        return f"Quận {s}"
    if s in _OUTER_HUYEN:
        return f"Huyện {s}"
    return s


def normalize_direction(value: Optional[str]) -> Optional[str]:
    """Chuẩn hóa hướng nhà về 8 hướng chính.

    "Đông - Nam" → "Đông Nam", "Tây" → "Tây", None → None.
    Nếu giá trị đã chuẩn (không có dấu "-") thì trả về nguyên.
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if s in _KNOWN_DIRECTIONS:
        return s
    parts = _DIR_SPLIT_RE.split(s)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    return " ".join(parts)


def filter_outliers(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lọc bỏ các dòng outlier và trả về (cleaned_df, log_df).

    Quy tắc:
    - area_m2 < 5 hoặc > 1000 → drop
    - total_price < 100_000_000 → drop (chắc chắn sai)
    - bedrooms > 15 → drop

    log_df có cột: listing_id, issue_type, original_value, decision.
    """
    log_rows: list[dict] = []
    keep_mask = pd.Series(True, index=df.index)

    if "area_m2" in df.columns:
        bad = (df["area_m2"] < 5) | (df["area_m2"] > 1000)
        for idx in df.index[bad]:
            log_rows.append(
                {
                    "listing_id": int(df.at[idx, "listing_id"]) if "listing_id" in df.columns else -1,
                    "issue_type": "area_too_small_or_large",
                    "original_value": float(df.at[idx, "area_m2"]),
                    "decision": "drop",
                }
            )
        keep_mask &= ~bad

    if "total_price" in df.columns:
        bad = df["total_price"] < 100_000_000
        for idx in df.index[bad & keep_mask]:
            log_rows.append(
                {
                    "listing_id": int(df.at[idx, "listing_id"]) if "listing_id" in df.columns else -1,
                    "issue_type": "price_too_low",
                    "original_value": float(df.at[idx, "total_price"]),
                    "decision": "drop",
                }
            )
        keep_mask &= ~bad

    if "bedrooms" in df.columns:
        bad = df["bedrooms"] > 15
        for idx in df.index[bad & keep_mask]:
            log_rows.append(
                {
                    "listing_id": int(df.at[idx, "listing_id"]) if "listing_id" in df.columns else -1,
                    "issue_type": "bedrooms_outlier",
                    "original_value": float(df.at[idx, "bedrooms"]),
                    "decision": "drop",
                }
            )
        keep_mask &= ~bad

    log_df = pd.DataFrame(log_rows, columns=["listing_id", "issue_type", "original_value", "decision"])
    return df[keep_mask].copy(), log_df


def recompute_price_per_m2(df: pd.DataFrame) -> pd.DataFrame:
    """Tính lại `price_per_m2 = total_price / area_m2` (ghi đè cột cũ)."""
    out = df.copy()
    if "total_price" in out.columns and "area_m2" in out.columns:
        out["price_per_m2"] = out["total_price"] / out["area_m2"]
    return out


def clean_dataframe(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Pipeline làm sạch: chuẩn hóa + lọc outlier + tính lại price_per_m2.

    Trả về: (cleaned_df, cleaning_log, errors).
    `errors` là list[str] mô tả vấn đề cấu trúc (không phải dòng dữ liệu).
    """
    errors: list[str] = []

    out = df.copy()

    if "district" in out.columns:
        out["district_clean"] = out["district"].apply(normalize_district)
        n_missing = int(out["district_clean"].isna().sum())
        if n_missing:
            errors.append(f"{n_missing} dòng thiếu district sau chuẩn hóa")
    else:
        errors.append("Thiếu cột 'district'")
        out["district_clean"] = None

    if "house_direction" in out.columns:
        out["direction_clean"] = out["house_direction"].apply(normalize_direction)
    else:
        errors.append("Thiếu cột 'house_direction'")
        out["direction_clean"] = None

    cleaned, log = filter_outliers(out)
    cleaned = recompute_price_per_m2(cleaned)
    return cleaned, log, errors