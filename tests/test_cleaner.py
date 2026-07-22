"""Test cho `src.cleaner` — các quy tắc chuẩn hóa dữ liệu BĐS."""

from __future__ import annotations

import pandas as pd
import pytest


def test_normalize_district_number_to_quan():
    from src.cleaner import normalize_district

    assert normalize_district("1") == "Quận 1"
    assert normalize_district("12") == "Quận 12"
    assert normalize_district("Bình Thạnh") == "Quận Bình Thạnh"
    assert normalize_district("Củ Chi") == "Huyện Củ Chi"
    assert normalize_district("Hóc Môn") == "Huyện Hóc Môn"
    assert normalize_district("") is None
    assert normalize_district(None) is None


def test_normalize_direction_compound_to_canonical():
    from src.cleaner import normalize_direction

    assert normalize_direction("Đông - Nam") == "Đông Nam"
    assert normalize_direction("Tây") == "Tây"
    assert normalize_direction("Đông - Bắc") == "Đông Bắc"
    assert normalize_direction("Tây - Nam") == "Tây Nam"
    assert normalize_direction(None) is None


def test_filter_outliers_drops_known_bad_rows():
    from src.cleaner import filter_outliers

    # Row index:
    #   0 — area=80, price=8e9, bedrooms=3     OK (keep)
    #   1 — area=4                          area_too_small_or_large  (drop)
    #   2 — area=80, price=8e9, bedrooms=3   OK (keep)
    #   3 — area=2000                       area_too_small_or_large  (drop)
    #   4 — area=80, price=5e7, bedrooms=50  price_too_low            (drop)
    df = pd.DataFrame(
        {
            "listing_id": [1, 2, 3, 4, 5],
            "area_m2": [80.0, 4.0, 80.0, 2000.0, 80.0],
            "total_price": [8e9, 8e9, 8e9, 8e9, 5e7],
            "bedrooms": [3, 3, 3, 3, 50],
        }
    )
    cleaned, log = filter_outliers(df)
    assert len(cleaned) == 2
    assert len(log) == 3
    issue_types = set(log["issue_type"])
    assert issue_types == {"area_too_small_or_large", "price_too_low"}
    # bedrooms_outlier KHÔNG xuất hiện vì dòng 4 đã bị drop ở bước price_too_low trước
    assert "bedrooms_outlier" not in issue_types


def test_recompute_price_per_m2():
    from src.cleaner import recompute_price_per_m2

    df = pd.DataFrame({"total_price": [8e9, 5e9], "area_m2": [80.0, 50.0]})
    out = recompute_price_per_m2(df)
    assert out["price_per_m2"].iloc[0] == 100_000_000.0
    assert out["price_per_m2"].iloc[1] == 100_000_000.0


def test_clean_dataframe_full_pipeline():
    from src.cleaner import clean_dataframe

    df = pd.DataFrame(
        {
            "listing_id": [1, 2, 3, 4],
            "district": ["1", "Bình Thạnh", "Củ Chi", None],
            "house_direction": ["Đông", "Đông - Nam", "Tây", None],
            "total_price": [8e9, 5e9, 8e9, 5e7],
            "area_m2": [80.0, 60.0, 70.0, 80.0],
            "bedrooms": [3, 2, 3, 50],
        }
    )
    out, log, errors = clean_dataframe(df)
    assert "district_clean" in out.columns
    assert "direction_clean" in out.columns
    assert out["district_clean"].iloc[0] == "Quận 1"
    assert out["district_clean"].iloc[1] == "Quận Bình Thạnh"
    assert out["district_clean"].iloc[2] == "Huyện Củ Chi"
    assert out["direction_clean"].iloc[0] == "Đông"
    assert out["direction_clean"].iloc[1] == "Đông Nam"
    assert out["direction_clean"].iloc[2] == "Tây"
    assert "price_per_m2" in out.columns
    assert out["price_per_m2"].iloc[0] == 100_000_000.0
    assert len(out) == 3  # 1 dropped (price_too_low), 3 kept
    # errors có thể rỗng nếu mọi cột cần thiết đều tồn tại