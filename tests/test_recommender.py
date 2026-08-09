"""Test cho `src.recommender.RecommendationEngine`."""

from __future__ import annotations

import pandas as pd


def _make_listings():
    """Fixture 6 căn hộ tại 4 quận (trong phạm vi data căn hộ)."""
    return pd.DataFrame(
        {
            "listing_id": [1, 2, 3, 4, 5, 6],
            "district_clean": [
                "Quận 7", "Quận 7", "Thành phố Thủ Đức", "Quận Bình Thạnh",
                "Quận Bình Thạnh", "Quận Gò Vấp",
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
    assert len(recs) == 2
    assert recs["listing_id"].tolist() == [1, 3]


def test_recommend_prefers_preferred_districts():
    from src.recommender import RecommendationEngine

    eng = RecommendationEngine()
    recs = eng.recommend(
        _make_listings(),
        budget_vnd=10e9,
        target_bedrooms=3,
        target_area_m2=75.0,
        preferred_districts=["Quận 7"],
        top_k=3,
    )
    districts = recs["district_clean"].tolist()
    assert all(d == "Quận 7" for d in districts)


def test_recommend_uses_segment_bonus():
    from src.recommender import RecommendationEngine

    listings = _make_listings()
    eng = RecommendationEngine()

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
        budget_vnd=100e6,
        target_bedrooms=2,
        target_area_m2=50.0,
        preferred_districts=[],
        top_k=5,
    )
    assert len(recs) == 0


def test_recommend_uses_thu_duc_district():
    """Test với tên quận 'Thành phố Thủ Đức' (sau sáp nhập 2021)."""
    from src.recommender import RecommendationEngine

    eng = RecommendationEngine()
    recs = eng.recommend(
        _make_listings(),
        budget_vnd=10e9,
        target_bedrooms=3,
        target_area_m2=70.0,
        preferred_districts=["Thành phố Thủ Đức"],
        top_k=3,
    )
    districts = recs["district_clean"].tolist()
    assert all(d == "Thành phố Thủ Đức" for d in districts)
