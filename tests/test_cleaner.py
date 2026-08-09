"""Test cho `src.cleaner` — các quy tắc chuẩn hóa dữ liệu BĐS căn hộ."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# --------------------------- normalize_district ---------------------------

def test_normalize_district_passthrough():
    """District trong xlsx đã ở dạng chu�n — pass-through + strip."""
    from src.cleaner import normalize_district

    assert normalize_district("Quận Bình Thạnh") == "Quận Bình Thạnh"
    assert normalize_district("Thành phố Thủ Đức") == "Thành phố Thủ Đức"
    assert normalize_district("Quận 7") == "Quận 7"
    assert normalize_district("Quận Gò Vấp") == "Quận Gò Vấp"
    assert normalize_district("") is None
    assert normalize_district(None) is None
    assert normalize_district("  Quận 7  ") == "Quận 7"


# --------------------------- normalize_direction --------------------------

def test_normalize_direction_decodes_codes():
    """Mã 1..8 → tên hướng chính."""
    from src.cleaner import normalize_direction

    assert normalize_direction(1.0) == "Đông"
    assert normalize_direction(2) == "Tây"
    assert normalize_direction(3) == "Nam"
    assert normalize_direction(4) == "Bắc"
    assert normalize_direction(5.0) == "Đông Nam"
    assert normalize_direction(6.0) == "Tây Nam"
    assert normalize_direction(7.0) == "Đông Bắc"
    assert normalize_direction(8.0) == "Tây Bắc"


def test_normalize_direction_handles_invalid():
    from src.cleaner import normalize_direction

    assert normalize_direction(None) is None
    assert normalize_direction(float("nan")) is None
    assert normalize_direction(99) is None
    assert normalize_direction("abc") is None


# --------------------------- decode_furnishing / decode_legal --------------

def test_decode_furnishing_labels():
    from src.cleaner import decode_furnishing

    assert decode_furnishing(1) == "Không nội thất"
    assert decode_furnishing(2) == "Nội thất cơ bản"
    assert decode_furnishing(3) == "Nội thất đầy đủ"
    assert decode_furnishing(4) == "Nội thất cao cấp"
    assert decode_furnishing(None) is None
    assert decode_furnishing(float("nan")) is None
    assert decode_furnishing(5) is None  # ngoài range


def test_decode_legal_labels():
    from src.cleaner import decode_legal

    assert decode_legal(1) == "Đang cập nhật"
    assert decode_legal(2) == "Sổ hồng lâu dài"
    assert decode_legal(4) == "Hợp đồng mua bán"
    assert decode_legal(5) == "Sổ hồng chung"
    assert decode_legal(6) == "Sổ hồng riêng"
    assert decode_legal(None) is None
    assert decode_legal(3) is None  # mã 3 không có → trả None


# --------------------------- filter_outliers -------------------------------

def test_filter_outliers_drops_known_bad_rows():
    """Test rule căn hộ: area < 10 hoặc > 500 → drop; price < 100tr → drop; bedrooms > 10 → drop."""
    from src.cleaner import filter_outliers

    df = pd.DataFrame(
        {
            "listing_id": [1, 2, 3, 4, 5, 6],
            "area_m2": [80.0, 5.0, 80.0, 800.0, 80.0, 80.0],
            "total_price": [8e9, 8e9, 8e9, 8e9, 5e7, 8e9],
            "bedrooms": [3, 3, 3, 3, 50, 3],
        }
    )
    cleaned, log = filter_outliers(df)
    # Row 1: area=5 → drop; Row 3: area=800 → drop; Row 4: price=5e7 → drop
    # Row 5: bedrooms=50 nhưng đã drop vì price trước đó
    assert len(cleaned) == 3  # row 0, 2, 5 (giữ)
    assert len(log) == 3
    issue_types = set(log["issue_type"])
    assert "area_out_of_range" in issue_types
    assert "price_too_low" in issue_types


# --------------------------- recompute_price_per_m2 ------------------------

def test_recompute_price_per_m2_basic():
    from src.cleaner import recompute_price_per_m2

    df = pd.DataFrame({"total_price": [8e9, 5e9], "area_m2": [80.0, 50.0]})
    out = recompute_price_per_m2(df)
    assert out["price_per_m2"].iloc[0] == 100_000_000.0
    assert out["price_per_m2"].iloc[1] == 100_000_000.0


def test_recompute_price_per_m2_handles_zero_area():
    from src.cleaner import recompute_price_per_m2

    df = pd.DataFrame({"total_price": [8e9, 5e9], "area_m2": [80.0, 0.0]})
    out = recompute_price_per_m2(df)
    assert out["price_per_m2"].iloc[0] == 100_000_000.0
    assert pd.isna(out["price_per_m2"].iloc[1])


# --------------------------- clean_dataframe full --------------------------

def test_clean_dataframe_full_pipeline():
    from src.cleaner import clean_dataframe

    df = pd.DataFrame(
        {
            "listing_id": [1, 2, 3, 4, 5],
            "district": ["Quận Bình Thạnh", "Thành phố Thủ Đức", "Quận 7", None, "Quận 12"],
            "direction": [5.0, 1.0, 8.0, float("nan"), 2.0],
            "furnishing_status": [3.0, 2.0, 1.0, float("nan"), 4.0],
            "legal_status": [6.0, 5.0, 2.0, float("nan"), 6.0],
            "total_price": [8e9, 5e9, 8e9, 5e7, 4e9],
            "area_m2": [80.0, 60.0, 70.0, 80.0, 65.0],
            "bedrooms": [3, 2, 3, 50, 2],
        }
    )
    out, log, errors = clean_dataframe(df)
    assert "district_clean" in out.columns
    assert "direction_clean" in out.columns
    assert "furnishing_label" in out.columns
    assert "legal_label" in out.columns
    assert "direction_code" in out.columns
    assert "furnishing_code" in out.columns
    assert "legal_code" in out.columns
    assert out["district_clean"].iloc[0] == "Quận Bình Thạnh"
    assert out["direction_clean"].iloc[0] == "Đông Nam"
    assert out["direction_clean"].iloc[1] == "Đông"
    assert out["furnishing_label"].iloc[0] == "Nội thất đầy đủ"
    assert out["legal_label"].iloc[0] == "Sổ hồng riêng"
    assert "price_per_m2" in out.columns
    assert out["price_per_m2"].iloc[0] == 100_000_000.0
    # Row 3 (price_too_low) drop → còn 4 dòng
    assert len(out) == 4
