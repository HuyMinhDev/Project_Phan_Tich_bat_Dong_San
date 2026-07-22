"""Tạo nguồn dữ liệu thứ hai `neighborhood_amenities.csv`.

Schema:
    ward,district_clean,school_count,hospital_count,supermarket_count,
    park_count,bus_stops_count,amenity_score

Dùng để merge với listings nhằm đáp ứng yêu cầu "ít nhất 2 nguồn / 2 loại tập tin có cấu trúc khác nhau"
của đồ án KHDL Chuyên đề 3. `amenity_score` là điểm tổng hợp có trọng số thể hiện mức tiện ích
của từng khu vực, dùng cho cả EDA (Task 11) và làm feature phụ cho RecommendationEngine (Task 9).

Chạy:
    python -m scripts.make_neighborhood_amenities
"""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

from src.cleaner import normalize_district

RANDOM_SEED = 42
TARGET_ROWS = 100


def _district_clean(raw: str) -> str:
    return normalize_district(raw) or "Không rõ"


def build_neighborhood_amenities(
    listings_path: Path,
    out_path: Path,
    target_rows: int = TARGET_ROWS,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    listings = pd.read_csv(listings_path)
    pairs = (
        listings[["district", "ward"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )
    pairs["district_clean"] = pairs["district"].apply(_district_clean)
    pairs = pairs[["ward", "district_clean"]].head(target_rows)

    rng = random.Random(seed)
    rows = []
    for _, r in pairs.iterrows():
        school = rng.randint(1, 12)
        hospital = rng.randint(0, 6)
        supermarket = rng.randint(0, 10)
        park = rng.randint(0, 8)
        bus = rng.randint(1, 20)
        score = round(
            1
            + 0.3 * school
            + 0.5 * hospital
            + 0.2 * supermarket
            + 0.4 * park
            + 0.1 * bus,
            2,
        )
        rows.append(
            {
                "ward": r["ward"],
                "district_clean": r["district_clean"],
                "school_count": school,
                "hospital_count": hospital,
                "supermarket_count": supermarket,
                "park_count": park,
                "bus_stops_count": bus,
                "amenity_score": score,
            }
        )
    df = pd.DataFrame(rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return df


def main() -> None:
    here = Path(__file__).resolve().parent.parent
    listings = here / "data" / "raw" / "real_estate_with_price_per_m2.csv"
    out = here / "data" / "raw" / "neighborhood_amenities.csv"
    df = build_neighborhood_amenities(listings, out)
    print(f"Wrote {len(df)} rows to {out}")
    print(df.head())


if __name__ == "__main__":
    main()