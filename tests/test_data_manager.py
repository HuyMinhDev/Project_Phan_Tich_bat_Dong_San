"""Test cho `src.data_manager.PropertyDataManager`."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


def test_load_csv_returns_dataframe(tmp_path: Path):
    from src.data_manager import PropertyDataManager

    csv = tmp_path / "x.csv"
    csv.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    mgr = PropertyDataManager(csv)
    df = mgr.load_raw()
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 2


def test_load_raw_missing_file_raises(tmp_path: Path):
    from src.data_manager import PropertyDataManager

    mgr = PropertyDataManager(tmp_path / "missing.csv")
    with pytest.raises(FileNotFoundError):
        mgr.load_raw()


def test_clean_pipeline_runs(tmp_path: Path):
    from src.data_manager import PropertyDataManager

    csv = tmp_path / "raw.csv"
    csv.write_text(
        "listing_id,district,house_direction,total_price,area_m2,bedrooms\n"
        "1,1,Đông,8000000000,80,3\n"
        "2,Bình Thạnh,Đông - Nam,5000000000,60,2\n"
        "3,Củ Chi,Tây,8000000000,70,3\n"
        "4,1,Đông,50000000,80,50\n",
        encoding="utf-8",
    )
    mgr = PropertyDataManager(csv)
    raw = mgr.load_raw()
    cleaned, log, errors = mgr.clean()
    assert "district_clean" in cleaned.columns
    assert "direction_clean" in cleaned.columns
    assert "price_per_m2" in cleaned.columns
    assert len(cleaned) == 3  # dòng 4 drop vì giá thấp
    assert len(log) >= 1
    assert isinstance(errors, list)


def test_merge_amenities_left_join():
    from src.data_manager import PropertyDataManager

    mgr = PropertyDataManager(Path("dummy.csv"))
    listings = pd.DataFrame(
        {
            "listing_id": [1, 2],
            "district_clean": ["Quận 1", "Quận 2"],
            "ward": ["Bến Nghé", "Tân Định"],
            "price_per_m2": [100e6, 80e6],
        }
    )
    amenities = pd.DataFrame(
        {
            "district_clean": ["Quận 1", "Quận 2"],
            "ward": ["Bến Nghé", "Tân Định"],
            "amenity_score": [5.0, 3.0],
        }
    )
    merged = mgr.merge_amenities(listings, amenities)
    assert "amenity_score" in merged.columns
    assert merged.loc[merged["listing_id"] == 1, "amenity_score"].iloc[0] == 5.0
    assert merged.loc[merged["listing_id"] == 2, "amenity_score"].iloc[0] == 3.0


def test_merge_amenities_left_join_keeps_unmatched():
    from src.data_manager import PropertyDataManager

    mgr = PropertyDataManager(Path("dummy.csv"))
    listings = pd.DataFrame(
        {
            "listing_id": [1, 2],
            "district_clean": ["Quận 1", "Quận 99"],
            "ward": ["Bến Nghé", "Unknown"],
            "price_per_m2": [100e6, 80e6],
        }
    )
    amenities = pd.DataFrame(
        {
            "district_clean": ["Quận 1"],
            "ward": ["Bến Nghé"],
            "amenity_score": [5.0],
        }
    )
    merged = mgr.merge_amenities(listings, amenities)
    assert len(merged) == 2
    # listing 2 không có amenity → NaN
    assert pd.isna(merged.loc[merged["listing_id"] == 2, "amenity_score"].iloc[0])


def test_save_cleaned_writes_csv(tmp_path: Path):
    from src.data_manager import PropertyDataManager

    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    log = pd.DataFrame({"issue_type": ["x"], "decision": ["drop"]})
    out = tmp_path / "out.csv"
    log_out = tmp_path / "log.csv"
    err_out = tmp_path / "err.txt"
    mgr = PropertyDataManager(tmp_path / "raw.csv")
    mgr.save_cleaned(df, log, out, log_out, err_out, errors=[])
    assert out.exists()
    assert log_out.exists()
    assert err_out.exists()
    assert pd.read_csv(out).shape == (2, 2)