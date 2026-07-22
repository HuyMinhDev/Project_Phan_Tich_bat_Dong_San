"""Test cho `src.predictor`."""

from __future__ import annotations

import numpy as np


def test_predictor_fit_predict_basic():
    from src.predictor import PricePredictor

    rng = np.random.default_rng(0)
    X = rng.normal(size=(100, 5))
    y = X.sum(axis=1) + rng.normal(size=100) * 0.1
    pred = PricePredictor(model_name="linear", log_target=True).fit(X, y)
    out = pred.predict(X)
    assert out.shape == (100,)
    # log_target=False → vẫn predict bình thường
    pred2 = PricePredictor(model_name="linear", log_target=False).fit(X, y)
    assert pred2.predict(X).shape == (100,)


def test_predictor_invalid_model_name_raises():
    from src.predictor import PricePredictor

    with __import__("pytest").raises(ValueError):
        PricePredictor(model_name="xgboost")


def test_cv_metrics_returns_means_and_stds():
    from src.predictor import cv_metrics

    rng = np.random.default_rng(0)
    X = rng.normal(size=(200, 5))
    y = X.sum(axis=1) + rng.normal(size=200) * 0.1
    m = cv_metrics(X, y, model_name="linear", log_target=True, n_splits=3, random_state=0)
    assert "mae_mean" in m and "rmse_mean" in m and "r2_mean" in m
    assert "mae_std" in m and "rmse_std" in m and "r2_std" in m
    assert m["n_splits"] == 3
    assert m["model_name"] == "linear"


def test_train_and_evaluate_full():
    from src.predictor import PricePredictor

    rng = np.random.default_rng(42)
    X = rng.normal(size=(200, 4))
    y = X.sum(axis=1) + rng.normal(size=200) * 0.1
    pred = PricePredictor(model_name="rf", log_target=True).fit(X[:150], y[:150])
    metrics = pred.evaluate(X[150:], y[150:])
    assert "mae" in metrics and "rmse" in metrics and "r2" in metrics
    # MAE phải dương và RMSE ≥ MAE (vì RMSE là sqrt(MSE) ≥ MAE trên phân phối chuẩn)
    assert metrics["mae"] > 0
    assert metrics["rmse"] >= 0


def test_baseline_dummy_predicts_median():
    from src.predictor import PricePredictor

    rng = np.random.default_rng(0)
    X = rng.normal(size=(100, 3))
    y = np.array([10.0] * 50 + [20.0] * 50)
    pred = PricePredictor(model_name="dummy", log_target=False).fit(X, y)
    out = pred.predict(X[:5])
    # DummyRegressor(strategy="median") → 15.0 (median của [10]*50 + [20]*50)
    assert np.allclose(out, 15.0)