"""PricePredictor — mô hình dự đoán giá/m².

Hỗ trợ 4 mô hình:
- `dummy`   : DummyRegressor(median) — baseline
- `linear`  : LinearRegression
- `rf`      : RandomForestRegressor
- `gbr`     : GradientBoostingRegressor

`log_target=True` (mặc định) → fit trên log1p(y), inverse bằng expm1.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold


_VALID_MODELS = {"dummy", "linear", "rf", "gbr"}


def _build_model(model_name: str, random_state: int) -> Any:
    if model_name == "dummy":
        return DummyRegressor(strategy="median")
    if model_name == "linear":
        return LinearRegression()
    if model_name == "rf":
        return RandomForestRegressor(
            n_estimators=200, max_depth=None, min_samples_leaf=2,
            n_jobs=-1, random_state=random_state,
        )
    if model_name == "gbr":
        return GradientBoostingRegressor(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            random_state=random_state,
        )
    raise ValueError(f"model_name không hợp lệ: {model_name}. Chọn một trong {_VALID_MODELS}")


def _maybe_log(y: np.ndarray, transform: bool) -> np.ndarray:
    if not transform:
        return y
    y = np.asarray(y, dtype=float)
    if np.any(y < 0):
        # log1p không xác định cho y < -1; clip về 0 để không NaN
        y = np.clip(y, 0.0, None)
    return np.log1p(y)


def _maybe_inverse(y: np.ndarray, transform: bool) -> np.ndarray:
    return np.expm1(y) if transform else y


class PricePredictor:
    def __init__(self, model_name: str = "linear", log_target: bool = True, random_state: int = 42) -> None:
        if model_name not in _VALID_MODELS:
            raise ValueError(
                f"model_name không hợp lệ: {model_name}. Chọn một trong {_VALID_MODELS}"
            )
        self.model_name = model_name
        self.log_target = log_target
        self.random_state = random_state
        self.model_ = _build_model(model_name, random_state)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "PricePredictor":
        y_t = _maybe_log(np.asarray(y, dtype=float), self.log_target)
        self.model_.fit(np.asarray(X), y_t)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        pred_t = self.model_.predict(np.asarray(X))
        return _maybe_inverse(np.asarray(pred_t, dtype=float), self.log_target)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> dict[str, float]:
        y_pred = self.predict(X)
        y_true = np.asarray(y, dtype=float)
        return {
            "mae": float(mean_absolute_error(y_true, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "r2": float(r2_score(y_true, y_pred)),
        }


def cv_metrics(
    X: np.ndarray,
    y: np.ndarray,
    model_name: str = "linear",
    log_target: bool = True,
    n_splits: int = 5,
    random_state: int = 42,
) -> dict[str, Any]:
    """5-fold CV trên train, trả về mean ± std của MAE/RMSE/R² trên thang gốc."""
    X = np.asarray(X)
    y = np.asarray(y, dtype=float)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    maes: list[float] = []
    rmses: list[float] = []
    r2s: list[float] = []
    for train_idx, test_idx in kf.split(X):
        pred = PricePredictor(model_name, log_target, random_state).fit(X[train_idx], y[train_idx])
        m = pred.evaluate(X[test_idx], y[test_idx])
        maes.append(m["mae"])
        rmses.append(m["rmse"])
        r2s.append(m["r2"])
    return {
        "model_name": model_name,
        "log_target": log_target,
        "n_splits": n_splits,
        "mae_mean": float(np.mean(maes)),
        "mae_std": float(np.std(maes)),
        "rmse_mean": float(np.mean(rmses)),
        "rmse_std": float(np.std(rmses)),
        "r2_mean": float(np.mean(r2s)),
        "r2_std": float(np.std(r2s)),
    }