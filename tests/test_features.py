"""Test cho `src.features`."""

from __future__ import annotations

import pandas as pd


def test_build_preprocessor_columns():
    from src.features import build_preprocessor

    numeric = ["area_m2", "bedrooms", "bathrooms", "floor_count", "frontage_width"]
    categorical = ["district_clean", "direction_clean"]
    pre = build_preprocessor(numeric, categorical)
    names = [name for name, _, _ in pre.transformers]
    assert "num" in names and "cat" in names


def test_transform_handles_missing():
    from src.features import build_preprocessor

    pre = build_preprocessor(["a"], ["b"])
    df = pd.DataFrame({"a": [1.0, None, 3.0], "b": ["x", None, "z"]})
    out = pre.fit_transform(df)
    assert out.shape[0] == 3
    assert out.shape[1] >= 2  # 1 numeric + ≥1 OHE


def test_transform_unknown_category_ignored():
    from src.features import build_preprocessor

    pre = build_preprocessor(["a"], ["b"])
    train = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": ["x", "y", "x"]})
    pre.fit(train)
    test = pd.DataFrame({"a": [4.0], "b": ["unknown_xyz"]})
    out = pre.transform(test)
    assert out.shape[0] == 1
    # vì handle_unknown="ignore" + min_frequency, nên vẫn transform được
    assert out.shape[1] >= 2


def test_get_feature_names():
    from src.features import build_preprocessor, get_feature_names

    pre = build_preprocessor(["a"], ["b"])
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": ["x", "y", "x"]})
    pre.fit(df)
    names = get_feature_names(pre)
    assert "a" in names
    assert any(n.startswith("b_") for n in names)