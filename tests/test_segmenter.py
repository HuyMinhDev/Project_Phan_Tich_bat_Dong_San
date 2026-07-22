"""Test cho `src.segmenter`."""

from __future__ import annotations

import numpy as np


def test_pick_k_by_silhouette_finds_three_clusters():
    from src.segmenter import pick_k_by_silhouette

    rng = np.random.default_rng(0)
    # spacing=5 (lớn hơn scale=1) → 3 cụm tách biệt rõ
    X = np.vstack([rng.normal(loc=i * 5.0, scale=1.0, size=(100, 4)) for i in range(3)])
    best_k, scores = pick_k_by_silhouette(X, k_range=(2, 6), random_state=0)
    assert best_k == 3
    assert all(isinstance(v, float) for v in scores.values())
    assert set(scores.keys()) == {2, 3, 4, 5, 6}
    assert scores[3] >= scores[2]


def test_segmenter_assigns_labels():
    from src.segmenter import KMeansSegmenter

    rng = np.random.default_rng(0)
    X = np.vstack([rng.normal(loc=i, scale=0.5, size=(80, 4)) for i in range(3)])
    seg = KMeansSegmenter(n_clusters=3, random_state=0).fit(X)
    labels = seg.predict(X)
    assert labels.shape == (240,)
    assert set(labels.tolist()) == {0, 1, 2}
    assert seg.centers_.shape == (3, 4)


def test_segmenter_describe_returns_dataframe():
    from src.segmenter import KMeansSegmenter

    rng = np.random.default_rng(0)
    X = np.vstack([rng.normal(loc=i, scale=0.5, size=(80, 4)) for i in range(3)])
    seg = KMeansSegmenter(n_clusters=3, random_state=0).fit(X)
    desc = seg.describe_segments(X, feature_names=["a", "b", "c", "d"])
    assert desc.shape == (3, 4)
    assert list(desc.index) == [0, 1, 2]
    assert list(desc.columns) == ["a", "b", "c", "d"]