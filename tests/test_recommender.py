"""Test cho `src.recommender.RecommendationEngine`."""

from __future__ import annotations

import pandas as pd


def _make_listings():
    return pd.DataFrame(
        {
            "listing_id": [1, 2, 3, 4, 5, 6],
            "district_clean": [
                "Quận 1", "Quận 1", "Quận 2", "Quận 7", "Quận 7", "Huyện Củ Chi",
            ],
            "ward": ["A", "A", "B", "Tân Mỹ", "Tân Phong", "X"],
            "total_price": [10e9, 5e9, 8e9, 4e9, 6e9, 1.5e9],
            "area_m2": [80.0, 60.0, 70.0, 67.0, 80.0, 200.0],
            "bedrooms": [3, 2, 3, 2, 3, 2],
            "price_per_m2": [125e6, 83e6, 114e6, 60e6, 75e6, 7.5e6],
            "amenity_score": [4.0, 4.5, 3.0, 5.0, 4.2, 2.0],
            "cluster": [0, 0, 0, 1, 1, 2],
        }
    )


def test_recommend_filters_by_budget():
    from src.recommender import RecommendationEngine

    eng = RecommendationEngine()
    recs = eng.recommend(
        _make_listings(),
        budget_vnd=6e9,
        target_bedrooms=2,
        target_area_m2=60.0,
        preferred_districts=[],
        top_k=5,
    )
    ids = recs["listing_id"].tolist()
    # budget 6e9 ± 20% = [4.8e9, 7.2e9]; bedrooms 2 ± 1 = [1, 3]
    #   listing 1: 10e9, BR 3 → fail budget    (loại)
    #   listing 2: 5e9, BR 2 → pass            (giữ)
    #   listing 3: 8e9, BR 3 → fail budget    (loại)
    #   listing 4: 4e9, BR 2 → fail budget    (loại)
    #   listing 5: 6e9, BR 3 → pass            (giữ)
    #   listing 6: 1.5e9, BR 2 → fail budget  (loại)
    assert 1 not in ids and 3 not in ids and 4 not in ids and 6 not in ids
    assert 2 in ids and 5 in ids


def test_recommend_returns_top_k():
    from src.recommender import RecommendationEngine

    eng = RecommendationEngine()
    recs = eng.recommend(
        _make_listings(),
        budget_vnd=10e9,
        target_bedrooms=3,
        target_area_m2=75.0,
        preferred_districts=[],
        top_k=3,
    )
    # budget 10e9 ± 20% = [8e9, 12e9]; BR 3 ± 1 = [2, 4]
    #   listing 1: 10e9, BR 3 → pass
    #   listing 2: 5e9, BR 2 → fail budget
    #   listing 3: 8e9, BR 3 → pass (boundary)
    #   listing 5: 6e9, BR 3 → fail budget
    #   các dòng khác fail budget
    # → còn 2 ứng viên, top_k=3 vẫn chỉ trả 2
    assert len(recs) == 2
    assert recs["listing_id"].tolist() == [1, 3]  # theo sort score_total


def test_recommend_prefers_preferred_districts():
    from src.recommender import RecommendationEngine

    eng = RecommendationEngine()
    recs = eng.recommend(
        _make_listings(),
        budget_vnd=10e9,
        target_bedrooms=3,
        target_area_m2=75.0,
        preferred_districts=["Quận 1"],
        top_k=3,
    )
    districts = recs["district_clean"].tolist()
    assert all(d == "Quận 1" for d in districts)


def test_recommend_uses_segment_bonus():
    from src.recommender import RecommendationEngine

    listings = _make_listings()
    eng = RecommendationEngine()

    # Yêu cầu cụm 1, budget vừa đủ để cluster-1 dòng pass filter
    recs_a = eng.recommend(
        listings,
        budget_vnd=7e9,
        target_bedrooms=3,
        target_area_m2=75.0,
        preferred_districts=[],
        top_k=3,
        preferred_cluster=1,
    )
    # budget 7e9 ± 20% = [5.6e9, 8.4e9]; BR 3 ± 1 = [2, 4]
    #   listing 1: 10e9 → fail
    #   listing 3: 8e9, cluster 0 → pass, no bonus
    #   listing 5: 6e9, cluster 1 → pass, +0.3 bonus
    # → top 1 phải là 5
    assert len(recs_a) >= 1
    assert recs_a.iloc[0]["listing_id"] == 5
    assert recs_a.iloc[0]["score_segment"] == 0.3


def test_recommend_returns_score_components_column():
    from src.recommender import RecommendationEngine

    eng = RecommendationEngine()
    recs = eng.recommend(
        _make_listings(),
        budget_vnd=8e9,
        target_bedrooms=2,
        target_area_m2=70.0,
        preferred_districts=[],
        top_k=2,
    )
    assert "score_components" in recs.columns
    assert "score_total" in recs.columns
    assert isinstance(recs["score_components"].iloc[0], dict)


def test_recommend_empty_when_no_match():
    from src.recommender import RecommendationEngine

    eng = RecommendationEngine()
    recs = eng.recommend(
        _make_listings(),
        budget_vnd=100e6,  # budget rất nhỏ → không match dòng nào
        target_bedrooms=2,
        target_area_m2=50.0,
        preferred_districts=[],
        top_k=5,
    )
    assert len(recs) == 0