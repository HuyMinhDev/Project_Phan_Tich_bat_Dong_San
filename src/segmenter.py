"""KMeansSegmenter — phân cụm K-Means có scale trước + chọn K theo silhouette.

`pick_k_by_silhouette(X, k_range, random_state) → (best_k, scores)` chọn K trong
`k_range` có silhouette score cao nhất.

`KMeansSegmenter` wrapper quanh sklearn Pipeline(StandardScaler + KMeans).
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def pick_k_by_silhouette(
    X: np.ndarray,
    k_range: tuple[int, int] = (3, 7),
    random_state: int = 42,
) -> tuple[int, dict[int, float]]:
    """Chọn K tốt nhất theo silhouette score trong khoảng [k_min, k_max] (inclusive)."""
    X = np.asarray(X)
    k_min, k_max = k_range
    scores: dict[int, float] = {}
    for k in range(k_min, k_max + 1):  # inclusive cả 2 đầu
        pipe = Pipeline(
            [
                ("scale", StandardScaler()),
                ("km", KMeans(n_clusters=k, n_init=10, random_state=random_state)),
            ]
        )
        labels = pipe.fit_predict(X)
        if len(set(labels.tolist())) < 2:
            scores[k] = -1.0
            continue
        s = silhouette_score(X, labels)
        scores[k] = float(s)
    best_k = max(scores, key=scores.get)
    return best_k, scores


class KMeansSegmenter:
    def __init__(self, n_clusters: int = 3, random_state: int = 42) -> None:
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.pipe_: Pipeline | None = None
        self.centers_: np.ndarray | None = None

    def fit(self, X: np.ndarray) -> "KMeansSegmenter":
        X = np.asarray(X)
        self.pipe_ = Pipeline(
            [
                ("scale", StandardScaler()),
                ("km", KMeans(n_clusters=self.n_clusters, n_init=10, random_state=self.random_state)),
            ]
        )
        self.pipe_.fit(X)
        # centers_ ở thang đã scale → inverse_transform về thang gốc
        scaler: StandardScaler = self.pipe_.named_steps["scale"]
        centers_scaled = self.pipe_.named_steps["km"].cluster_centers_
        self.centers_ = scaler.inverse_transform(centers_scaled)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.pipe_ is None:
            raise RuntimeError("Chưa gọi fit() trước predict()")
        return self.pipe_.predict(np.asarray(X))

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        self.fit(X)
        return self.predict(X)

    def describe_segments(
        self, X: np.ndarray, feature_names: Iterable[str]
    ) -> pd.DataFrame:
        if self.pipe_ is None:
            raise RuntimeError("Chưa gọi fit() trước describe_segments()")
        labels = self.predict(X)
        df = pd.DataFrame(np.asarray(X), columns=list(feature_names))
        df["__cluster__"] = labels
        return df.groupby("__cluster__").mean()