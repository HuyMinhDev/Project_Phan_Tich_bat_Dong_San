"""Feature engineering pipeline.

`build_preprocessor(numeric_cols, categorical_cols)` trả về `ColumnTransformer`
gồm 2 nhánh:
- numeric: `SimpleImputer(median)` → `StandardScaler`
- categorical: `SimpleImputer(constant="missing")` → `OneHotEncoder(handle_unknown="ignore", min_frequency=10)`

`get_feature_names(ct)` trích tên feature sau khi fit (dùng cho EDA/K-Means).
"""

from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import _VectorizerMixin  # noqa: F401  (silence unused)
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def build_preprocessor(
    numeric_cols: list[str],
    categorical_cols: list[str],
) -> ColumnTransformer:
    numeric_pipe = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        [
            ("impute", SimpleImputer(strategy="constant", fill_value="missing")),
            ("ohe", OneHotEncoder(handle_unknown="ignore", min_frequency=10)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric_cols),
            ("cat", categorical_pipe, categorical_cols),
        ],
        remainder="drop",
        sparse_threshold=0.0,
    )


def get_feature_names(ct: ColumnTransformer) -> list[str]:
    """Trích tên feature sau khi `ct` đã fit. Trả về list[str]."""
    out: list[str] = []
    for name, trans, cols in ct.transformers_:
        if name == "remainder":
            continue
        if hasattr(trans, "get_feature_names_out"):
            sub = list(trans.get_feature_names_out(cols))
        else:
            sub = list(cols)
        out.extend(sub)
    return out