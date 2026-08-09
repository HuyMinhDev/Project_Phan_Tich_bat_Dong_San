"""Tạo nguồn dữ liệu thứ hai `neighborhood_amenities.csv` từ **OpenStreetMap qua Overpass API**.

Schema:
    ward, district_clean, school_count, hospital_count, supermarket_count,
    park_count, bus_stops_count, amenity_score

Dùng để merge với listings nhằm đáp ứng yêu cầu "ít nhất 2 nguồn / 2 loại tập tin có cấu trúc khác nhau"
của đồ án KHDL Chuyên đề 3. `amenity_score` là điểm tổng hợp có trọng số thể hiện mức tiện ích
của từng khu vực, dùng cho cả EDA (Task 11) và làm feature phụ cho RecommendationEngine (Task 9).

Dữ liệu: crawl từ **Overpass API (OpenStreetMap)** — dữ liệu thật, có timestamp OSM trong response.
Khi API lỗi/timeout → giá trị = 0.

Lưu ý kỹ thuật:
- Tên area trên OSM chỉ là "Quận X" (không có suffix thành phố).
- Dùng `out tags` để lấy element rồi tự đếm theo tag value (chính xác hơn `out count`).
- Mỗi quận = 1 request duy nhất (5 nhóm tiện ích trong 1 query union).

Chạy:
    python -m scripts.make_neighborhood_amenities
"""

from __future__ import annotations

import time
from collections import Counter
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

from src.cleaner import normalize_district

# Ánh xạ district_clean -> tên area trên OSM (chỉ phần "Quận X", không kèm TP)
DISTRICT_OSM_NAMES = {
    "Quận 7":            "Quận 7",
    "Quận 12":           "Quận 12",
    "Quận Bình Tân":     "Quận Bình Tân",
    "Quận Bình Thạnh":   "Quận Bình Thạnh",
    "Quận Gò Vấp":       "Quận Gò Vấp",
    "Thành phố Thủ Đức": "Thành phố Thủ Đức",
}

# Nhóm tiện ích: tên cột output -> (key OSM, set các value muốn đếm)
AMENITY_GROUPS = {
    "school_count":      ("amenity", {"school", "kindergarten"}),
    "hospital_count":    ("amenity", {"hospital", "clinic", "doctors"}),
    "supermarket_count": ("shop",    {"supermarket", "convenience"}),
    "park_count":        ("leisure", {"park", "garden"}),
    "bus_stops_count":   ("highway", {"bus_stop"}),
}

# Trọng số giữ nguyên như phiên bản cũ (đã thống nhất với EDA / recommender)
WEIGHTS = {
    "school_count":      0.3,
    "hospital_count":    0.5,
    "supermarket_count": 0.2,
    "park_count":        0.4,
    "bus_stops_count":   0.1,
}

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

USER_AGENT = "ChuoiKhoiUngDung-Research/1.0 (academic project; contact: minhhuy@example.com)"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
}


def _district_clean(raw: str) -> str:
    return normalize_district(raw) or "Không rõ"


def _build_union_query(district_osm_name: str) -> str:
    """Xây 1 Overpass query duy nhất, gom tất cả tag key trong union với regex."""
    safe = district_osm_name.replace('"', '\\"')

    # Gom tất cả key:value vào 1 regex duy nhất
    # Overpass cho phép: ["key"~"regex"](area.a) — match key có value thuộc regex
    # Nhưng để rõ ràng, ta tách theo từng key.
    lines = []
    for col_name, (key, values) in AMENITY_GROUPS.items():
        # value|value|value
        union = "|".join(values)
        # 3 union: node, way, relation
        lines.append(f'  node["{key}"~"^({union})$"](area.a);')
        lines.append(f'  way["{key}"~"^({union})$"](area.a);')
        lines.append(f'  relation["{key}"~"^({union})$"](area.a);')

    block = "\n".join(lines)

    return f"""
[out:json][timeout:90];
area["name"="{safe}"]->.a;
(
{block}
);
out tags;
"""


def _query_overpass(query: str, retries: int = 1, timeout: int = 100) -> Optional[dict]:
    """Gọi Overpass có retry ít + fallback endpoint."""
    last_err: Optional[Exception] = None
    for attempt in range(retries + 1):
        for endpoint in OVERPASS_ENDPOINTS:
            try:
                r = requests.post(
                    endpoint,
                    data={"data": query},
                    headers=HEADERS,
                    timeout=timeout,
                )
                if r.status_code == 200:
                    return r.json()
                elif r.status_code in (429, 502, 503, 504):
                    backoff = 4 * (attempt + 1)
                    print(f"[debug] {endpoint} → {r.status_code}, backoff {backoff}s")
                    time.sleep(backoff)
                    continue
                else:
                    print(f"[warn] {endpoint} status={r.status_code}: {r.text[:150]}")
                    return None
            except requests.RequestException as e:
                last_err = e
                time.sleep(2)
                continue
    print(f"[warn] Overpass failed: {last_err}")
    return None


def _tally_by_key(response: Optional[dict]) -> dict[str, Counter]:
    """Đếm elements theo từng OSM key.

    Trả về: {key_osm: Counter(value -> count)}
    """
    if not response:
        return {}
    by_key: dict[str, Counter] = {}
    for el in response.get("elements", []):
        tags = el.get("tags", {})
        for key in AMENITY_GROUPS.keys():
            osm_key, _ = AMENITY_GROUPS[key]
            if osm_key in tags:
                by_key.setdefault(osm_key, Counter())[tags[osm_key]] += 1
    return by_key


def _fetch_district_counts(district_osm_name: str) -> dict[str, int]:
    """Lấy 5 số đếm tiện ích cho 1 quận (1 query duy nhất)."""
    q = _build_union_query(district_osm_name)
    resp = _query_overpass(q, retries=1, timeout=100)
    by_key = _tally_by_key(resp)

    counts: dict[str, int] = {}
    for col_name, (osm_key, target_values) in AMENITY_GROUPS.items():
        c = by_key.get(osm_key, Counter())
        counts[col_name] = sum(c[v] for v in target_values)
    return counts


def build_neighborhood_amenities(
    listings_path: Path,
    out_path: Path,
    target_rows: int = 100,
) -> pd.DataFrame:
    """Crawl dữ liệu tiện ích THẬT từ OpenStreetMap, gộp theo (district_clean, ward)."""
    suffix = listings_path.suffix.lower()
    if suffix == ".csv":
        listings = pd.read_csv(listings_path)
    else:
        listings = pd.read_excel(listings_path)

    pairs = (
        listings[["district", "ward"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )
    pairs["district_clean"] = pairs["district"].apply(_district_clean)
    pairs = pairs[["ward", "district_clean"]].head(target_rows)

    # Cache: (district_clean) -> counts (mỗi quận gọi API 1 lần)
    district_cache: dict[str, dict[str, int]] = {}

    rows = []
    for _, r in pairs.iterrows():
        district_clean = r["district_clean"]
        if district_clean not in district_cache:
            osm_name = DISTRICT_OSM_NAMES.get(district_clean)
            if osm_name:
                print(f"[info] Crawling OSM data for: {district_clean} ({osm_name})")
                counts = _fetch_district_counts(osm_name)
                print(f"  → {counts}")
                district_cache[district_clean] = counts
            else:
                print(f"[warn] District not in OSM mapping: {district_clean} → 0")
                district_cache[district_clean] = {
                    "school_count": 0,
                    "hospital_count": 0,
                    "supermarket_count": 0,
                    "park_count": 0,
                    "bus_stops_count": 0,
                }

        counts = district_cache[district_clean]
        school      = counts.get("school_count", 0)
        hospital    = counts.get("hospital_count", 0)
        supermarket = counts.get("supermarket_count", 0)
        park        = counts.get("park_count", 0)
        bus         = counts.get("bus_stops_count", 0)

        score = round(
            1
            + WEIGHTS["school_count"]      * school
            + WEIGHTS["hospital_count"]    * hospital
            + WEIGHTS["supermarket_count"] * supermarket
            + WEIGHTS["park_count"]        * park
            + WEIGHTS["bus_stops_count"]   * bus,
            2,
        )

        rows.append(
            {
                "ward":             r["ward"],
                "district_clean":   district_clean,
                "school_count":     school,
                "hospital_count":   hospital,
                "supermarket_count": supermarket,
                "park_count":       park,
                "bus_stops_count":  bus,
                "amenity_score":    score,
            }
        )

    df = pd.DataFrame(rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return df


def main() -> None:
    here = Path(__file__).resolve().parent.parent
    listings = here / "data" / "raw" / "real_estate_apartment.xlsx"
    out = here / "data" / "raw" / "neighborhood_amenities.csv"
    df = build_neighborhood_amenities(listings, out)
    print(f"\nWrote {len(df)} rows to {out}")
    print(df.head().to_string())

    # Tổng kết theo quận (lấy distinct district để khỏi trùng)
    if not df.empty:
        print("\n=== amenity_score theo district_clean (mean, đã dedupe ward) ===")
        dedup = df.drop_duplicates(subset=["district_clean", "ward"])
        print(
            dedup.groupby("district_clean")["amenity_score"]
            .mean()
            .round(2)
            .sort_values(ascending=False)
            .to_string()
        )
        print("\n=== Tổng số ward unique theo district_clean ===")
        print(dedup.groupby("district_clean").size().to_string())


if __name__ == "__main__":
    main()