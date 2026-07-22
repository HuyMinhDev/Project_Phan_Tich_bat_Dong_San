"""PropertyDataManager — quản lý dữ liệu bất động sản.

Bao gồm:
- `load_raw()` — đọc CSV thô từ đường dẫn đã khởi tạo.
- `clean()` — áp dụng pipeline làm sạch (chuẩn hóa district/direction, lọc
  outlier, tính lại price_per_m2), trả về (cleaned_df, log_df, errors).
- `merge_amenities(listings, amenities)` — left-join theo (district_clean, ward).
- `save_cleaned(...)` — ghi CSV + log + error_log.txt.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.cleaner import clean_dataframe


class PropertyDataManager:
    def __init__(self, raw_path: Path | str) -> None:
        self.raw_path = Path(raw_path)

    def load_raw(self) -> pd.DataFrame:
        if not self.raw_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {self.raw_path}")
        return pd.read_csv(self.raw_path)

    def clean(self) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
        df = self.load_raw()
        return clean_dataframe(df)

    @staticmethod
    def merge_amenities(
        listings: pd.DataFrame, amenities: pd.DataFrame
    ) -> pd.DataFrame:
        """Left-join theo (district_clean, ward). Chỉ merge cột `amenity_score`.

        Nếu cùng (district, ward) xuất hiện nhiều dòng trong amenities → lấy mean.
        Nếu `amenities` rỗng hoặc thiếu cột `amenity_score` → trả về listings
        với cột `amenity_score` NaN.
        """
        if amenities.empty or "amenity_score" not in amenities.columns:
            listings = listings.copy()
            listings["amenity_score"] = float("nan")
            return listings
        agg = amenities.groupby(
            ["district_clean", "ward"], as_index=False
        )["amenity_score"].mean()
        merged = listings.merge(agg, on=["district_clean", "ward"], how="left")
        return merged

    @staticmethod
    def save_cleaned(
        cleaned: pd.DataFrame,
        log: pd.DataFrame,
        cleaned_path: Path | str,
        log_path: Path | str,
        error_path: Path | str,
        errors: list[str] | None = None,
    ) -> None:
        cleaned_path = Path(cleaned_path)
        log_path = Path(log_path)
        error_path = Path(error_path)
        cleaned_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        error_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(cleaned_path, index=False)
        log.to_csv(log_path, index=False)
        if not log.empty:
            log_text = (
                f"cleaning_log: {len(log)} dòng được ghi nhận là outlier/vấn đề\n"
            )
        else:
            log_text = "cleaning_log: không có outlier được ghi nhận\n"
        if errors:
            log_text += "errors:\n" + "\n".join(f"  - {e}" for e in errors) + "\n"
        error_path.write_text(log_text, encoding="utf-8")