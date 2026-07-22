"""RecommendationEngine — hệ gợi ý top 5 theo hồ sơ nhu cầu.

Chiến lược hybrid:
1. Filter cứng (loại trước khi chấm):
   - total_price ∈ [0.8*budget, 1.2*budget]
   - bedrooms ∈ [target_bedrooms-1, target_bedrooms+1]
   - district_clean ∈ preferred_districts (nếu không rỗng)
2. Scoring (cộng dồn):
   - price_score  = 1 - |Δprice_per_m2| / target_price_per_m2  (target = budget/target_area_m2)
   - area_score   = 1 - |Δarea_m2| / target_area_m2
   - segment_bonus = 0.3 nếu cùng cluster
   - amenity_bonus = 0.2 * (amenity_score / max_amenity)
3. Trả về top_k theo score_total giảm dần.

Đầu vào `listings` phải có các cột: listing_id, district_clean, ward, total_price,
area_m2, bedrooms, price_per_m2, amenity_score (NaN OK), cluster (NaN OK nếu
chưa chạy K-Means).
"""

from __future__ import annotations

import math
from typing import Optional

import numpy as np
import pandas as pd


class RecommendationEngine:
    BUDGET_TOLERANCE = 0.20
    BEDROOM_TOLERANCE = 1
    SEGMENT_BONUS = 0.3
    AMENITY_WEIGHT = 0.2

    def recommend(
        self,
        listings: pd.DataFrame,
        budget_vnd: float,
        target_bedrooms: int,
        target_area_m2: float,
        preferred_districts: list[str],
        top_k: int = 5,
        preferred_cluster: Optional[int] = None,
    ) -> pd.DataFrame:
        df = listings.copy()
        if df.empty:
            return df.assign(score_total=[], score_components=[])

        # 1. Filter cứng
        budget_min = budget_vnd * (1 - self.BUDGET_TOLERANCE)
        budget_max = budget_vnd * (1 + self.BUDGET_TOLERANCE)
        bedroom_min = target_bedrooms - self.BEDROOM_TOLERANCE
        bedroom_max = target_bedrooms + self.BEDROOM_TOLERANCE

        mask = (
            (df["total_price"] >= budget_min)
            & (df["total_price"] <= budget_max)
            & (df["bedrooms"] >= bedroom_min)
            & (df["bedrooms"] <= bedroom_max)
        )
        if preferred_districts:
            mask &= df["district_clean"].isin(preferred_districts)

        candidates = df[mask].copy()
        if candidates.empty:
            return candidates.assign(
                score_total=pd.Series(dtype=float),
                score_components=pd.Series(dtype=object),
            )

        # 2. Tính target price_per_m2 từ budget/target_area
        target_price_per_m2 = budget_vnd / max(target_area_m2, 1.0)
        max_amenity = (
            float(candidates["amenity_score"].max())
            if "amenity_score" in candidates.columns
            else None
        )
        if not math.isfinite(max_amenity) or max_amenity is None or max_amenity <= 0:
            max_amenity = None

        # 3. Tính điểm từng ứng viên
        price_diffs = np.abs(candidates["price_per_m2"].astype(float) - target_price_per_m2)
        price_scores = 1.0 - price_diffs / target_price_per_m2

        area_diffs = np.abs(candidates["area_m2"].astype(float) - target_area_m2)
        area_scores = 1.0 - area_diffs / max(target_area_m2, 1.0)

        if (
            "cluster" in candidates.columns
            and preferred_cluster is not None
        ):
            cluster_bonus = np.where(
                candidates["cluster"].fillna(-1).astype(int) == int(preferred_cluster),
                self.SEGMENT_BONUS,
                0.0,
            )
        else:
            cluster_bonus = np.zeros(len(candidates))

        if "amenity_score" in candidates.columns and max_amenity is not None:
            amen = candidates["amenity_score"].astype(float).fillna(0.0)
            amenity_bonus = self.AMENITY_WEIGHT * (amen / max_amenity)
        else:
            amenity_bonus = np.zeros(len(candidates))

        totals = price_scores + area_scores + cluster_bonus + amenity_bonus

        candidates = candidates.assign(
            score_price=price_scores,
            score_area=area_scores,
            score_segment=cluster_bonus,
            score_amenity=amenity_bonus,
            score_total=totals,
        )
        candidates["score_components"] = candidates.apply(
            lambda r: {
                "price": float(r["score_price"]),
                "area": float(r["score_area"]),
                "segment": float(r["score_segment"]),
                "amenity": float(r["score_amenity"]),
            },
            axis=1,
        )

        candidates = candidates.sort_values("score_total", ascending=False).head(top_k)
        return candidates.reset_index(drop=True)