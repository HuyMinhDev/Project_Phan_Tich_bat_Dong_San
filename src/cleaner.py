"""Các quy tắc chuẩn hóa dữ liệu BĐS căn hộ/chung cư TP.HCM.

Áp dụng cho `real_estate_apartment.xlsx` (schema chotot crawl):
1. `district` — data đã ở dạng text chuẩn ("Quận Bình Thạnh"); pass-through
   sau khi strip. Nếu cần map "Thành phố Thủ Đức" → giữ nguyên (đây là tên
   chính thức sau sáp nhập).
2. `direction` (mã số 1..8) → decode về 8 hướng chính tiếng Việt.
3. `balcony_direction` (mã số 1..8) → cùng cách decode.
4. `furnishing_status` (mã 1..4) → giữ mã (NaN OK), chỉ thêm tên gợi ý
   qua `_FURNISHING_LABELS`.
5. `legal_status` (mã 1,2,4,5,6) → giữ mã, decode nhãn qua `_LEGAL_LABELS`.
6. `total_price` — bỏ NaN và giá trị < 100 triệu (chắc chắn sai).
7. `area_m2` — bỏ dòng có diện tích < 10m² hoặc > 500m² (outlier rõ ràng
   cho căn hộ; data đã có 1 tin 1323m² — outlier).
8. `bedrooms` — bỏ dòng có số phòng > 10 (căn hộ hiếm khi > 10 phòng).
9. `price_per_m2` — tính lại từ `total_price / area_m2` để đảm bảo nhất
   quán (đề phòng data thô có giá/m² lệch).
"""

from __future__ import annotations

import re
from typing import Optional

import numpy as np
import pandas as pd


# Map mã hướng 1..8 → tên hư�ng chuẩn
_DIRECTION_CODE_TO_NAME = {
    1: "Đông",
    2: "Tây",
    3: "Nam",
    4: "Bắc",
    5: "Đông Nam",
    6: "Tây Nam",
    7: "Đông Bắc",
    8: "Tây Bắc",
}

# Nhãn tình trạng nội thất (mapping dựa trên phổ biến trên chotot)
_FURNISHING_LABELS = {
    1: "Không nội thất",
    2: "Nội thất cơ bản",
    3: "Nội thất đầy đủ",
    4: "Nội thất cao cấp",
}

# Nhãn tình trạng pháp lý (mã 3 vắng — có thể là đang cập nhật)
_LEGAL_LABELS = {
    1: "Đang cập nhật",
    2: "Sổ hồng lâu dài",
    4: "Hợp đồng mua bán",
    5: "Sổ hồng chung",
    6: "Sổ hồng riêng",
}


def normalize_district(value: Optional[str]) -> Optional[str]:
    """District đã chuẩn sẵn trong xlsx. Pass-through + strip.

    Trả về None nếu đầu vào rỗng/NaN.
    """
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    s = str(value).strip()
    if not s or s.lower() in {"nan", "none", "null"}:
        return None
    return s


def normalize_direction(value) -> Optional[str]:
    """Decode mã hướng 1..8 → tên hướng chính.

    Chấp nhận cả float (1.0) và int (1) và None. Trả về None nếu
    giá trị NaN hoặc không nằm trong map.
    """
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    try:
        code = int(float(value))
    except (TypeError, ValueError):
        return None
    return _DIRECTION_CODE_TO_NAME.get(code)


def decode_furnishing(value) -> Optional[str]:
    """Decode mã furnishing_status 1..4 → nhãn tiếng Việt. None nếu NaN/không rõ."""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    try:
        code = int(float(value))
    except (TypeError, ValueError):
        return None
    return _FURNISHING_LABELS.get(code)


def decode_legal(value) -> Optional[str]:
    """Decode mã legal_status 1,2,4,5,6 → nhãn tiếng Việt. None nếu NaN/không rõ."""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    try:
        code = int(float(value))
    except (TypeError, ValueError):
        return None
    return _LEGAL_LABELS.get(code)


def filter_outliers(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lọc bỏ các dòng outlier và trả về (cleaned_df, log_df).

    Quy tắc (điều chỉnh cho căn hộ):
    - area_m2 < 10 hoặc > 500  → drop (căn hộ hiếm khi < 10m² hoặc > 500m²)
    - total_price < 100_000_000 → drop (chắc chắn sai)
    - bedrooms > 10            → drop

    log_df có cột: listing_id, issue_type, original_value, decision.
    """
    log_rows: list[dict] = []
    keep_mask = pd.Series(True, index=df.index)

    if "area_m2" in df.columns:
        bad = (df["area_m2"] < 10) | (df["area_m2"] > 500)
        for idx in df.index[bad]:
            log_rows.append(
                {
                    "listing_id": int(df.at[idx, "listing_id"]) if "listing_id" in df.columns else -1,
                    "issue_type": "area_out_of_range",
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
        bad = df["bedrooms"] > 10
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
    """Tính lại `price_per_m2 = total_price / area_m2` (ghi đè cột cũ).

    Nếu total_price hoặc area_m2 NaN thì giữ price_per_m2 = NaN.
    """
    out = df.copy()
    if "total_price" in out.columns and "area_m2" in out.columns:
        area = out["area_m2"]
        # Chia an toàn: chỗ area <= 0 hoặc NaN → kết quả NaN
        with np.errstate(divide="ignore", invalid="ignore"):
            new_ppm2 = out["total_price"].astype(float) / area.astype(float)
        new_ppm2 = new_ppm2.where(area > 0)
        out["price_per_m2"] = new_ppm2
    return out


def clean_dataframe(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Pipeline làm sạch cho căn hộ: chuẩn hóa + lọc outlier + tính lại price_per_m2.

    Trả về: (cleaned_df, cleaning_log, errors).
    `errors` là list[str] mô tả vấn đề cấu trúc (không phải dòng dữ liệu).
    """
    errors: list[str] = []

    out = df.copy()

    # 1. district
    if "district" in out.columns:
        out["district_clean"] = out["district"].apply(normalize_district)
        n_missing = int(out["district_clean"].isna().sum())
        if n_missing:
            errors.append(f"{n_missing} dòng thiếu district sau chuẩn hóa")
    else:
        errors.append("Thiếu cột 'district'")
        out["district_clean"] = None

    # 2. direction (số 1..8 → text)
    if "direction" in out.columns:
        out["direction_clean"] = out["direction"].apply(normalize_direction)
    else:
        errors.append("Thiếu cột 'direction'")
        out["direction_clean"] = None

    # 3. furnishing + legal — chỉ thêm cột nhãn nếu có mã
    if "furnishing_status" in out.columns:
        out["furnishing_label"] = out["furnishing_status"].apply(decode_furnishing)
    if "legal_status" in out.columns:
        out["legal_label"] = out["legal_status"].apply(decode_legal)

    # 4. Copy mã categorical dạng số vào cleaned (cho ML dùng numeric)
    # direction (1..8) — nếu có cột gốc
    if "direction" in out.columns:
        out["direction_code"] = out["direction"]
    else:
        out["direction_code"] = np.nan
    # balcony_direction (1..8)
    if "balcony_direction" in out.columns:
        out["balcony_code"] = out["balcony_direction"]
    else:
        out["balcony_code"] = np.nan
    # furnishing_status (1..4)
    if "furnishing_status" in out.columns:
        out["furnishing_code"] = out["furnishing_status"]
    else:
        out["furnishing_code"] = np.nan
    # legal_status (1,2,4,5,6)
    if "legal_status" in out.columns:
        out["legal_code"] = out["legal_status"]
    else:
        out["legal_code"] = np.nan
    # apartment_type (1..6)
    if "apartment_type" in out.columns:
        out["apartment_type"] = out["apartment_type"]
    else:
        out["apartment_type"] = np.nan
    # image_count (int) — giữ nguyên
    if "image_count" in out.columns:
        out["image_count"] = out["image_count"]
    else:
        out["image_count"] = np.nan

    # 5. Lọc outlier + recompute price_per_m2
    cleaned, log = filter_outliers(out)
    cleaned = recompute_price_per_m2(cleaned)

    return cleaned, log, errors
