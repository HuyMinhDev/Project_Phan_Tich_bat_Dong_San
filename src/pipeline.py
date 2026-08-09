"""Pipeline CLI end-to-end cho đồ án KHDL chuyên đề 3 (căn hộ/chung cư).

Chạy:
    python -m src.pipeline \
        --data-path data/raw/real_estate_apartment.xlsx \
        --amenities-path data/raw/neighborhood_amenities.csv \
        --output-dir data/processed \
        --reports-dir reports

Sinh ra:
    data/processed/listings_clean.csv
    data/processed/listings_with_amenities.csv
    data/logs/cleaning_log.csv
    data/logs/error_log.txt
    reports/metrics.json
    reports/sample_recommendations.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.data_manager import PropertyDataManager
from src.features import build_preprocessor
from src.predictor import PricePredictor, cv_metrics
from src.recommender import RecommendationEngine
from src.segmenter import KMeansSegmenter, pick_k_by_silhouette


# Numeric features dùng cho ML — căn hộ: diện tích + phòng + mã categorical số
NUMERIC_COLS = [
    "area_m2",
    "bedrooms",
    "bathrooms",
    "direction_code",
    "balcony_code",
    "furnishing_code",
    "legal_code",
    "image_count",
    "apartment_type",
]
CATEGORICAL_COLS = ["district_clean", "direction_clean", "project_name"]
TARGET = "price_per_m2"
RANDOM_STATE = 42


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="KHDL pipeline — BĐS căn hộ TP.HCM")
    p.add_argument("--data-path", type=Path, default=Path("data/raw/real_estate_apartment.xlsx"))
    p.add_argument("--amenities-path", type=Path, default=Path("data/raw/neighborhood_amenities.csv"))
    p.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    p.add_argument("--logs-dir", type=Path, default=Path("data/logs"))
    p.add_argument("--reports-dir", type=Path, default=Path("reports"))
    p.add_argument("--test-size", type=float, default=0.2)
    p.add_argument("--k-range", type=int, nargs=2, default=[3, 6])
    return p


def _prepare_features(merged: pd.DataFrame) -> pd.DataFrame:
    """Đảm bảo tất cả cột feature tồn tại; điền NaN hợp lý cho numeric/categorical.

    Cột numeric NaN → median của tập (sẽ do Pipeline SimpleImputer xử lý,
    nhưng ta vẫn điền tạm để tránh drop dòng trong train_test_split).
    Cột categorical NaN → "missing" (Pipeline sẽ impute constant).
    """
    df = merged.copy()
    for col in NUMERIC_COLS:
        if col not in df.columns:
            df[col] = np.nan
    for col in CATEGORICAL_COLS:
        if col not in df.columns:
            df[col] = "missing"
    return df


def main() -> int:
    args = _build_argparser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.logs_dir.mkdir(parents=True, exist_ok=True)
    args.reports_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/8] Loading raw data from {args.data_path} ...")
    mgr = PropertyDataManager(args.data_path)
    raw = mgr.load_raw()
    print(f"      raw shape: {raw.shape}")

    print("[2/8] Cleaning data ...")
    cleaned, log, errors = mgr.clean()
    print(f"      cleaned shape: {cleaned.shape}; log rows: {len(log)}")
    cleaned_path = args.output_dir / "listings_clean.csv"
    log_path = args.logs_dir / "cleaning_log.csv"
    err_path = args.logs_dir / "error_log.txt"
    PropertyDataManager.save_cleaned(cleaned, log, cleaned_path, log_path, err_path, errors)

    print(f"[3/8] Loading + merging amenities from {args.amenities_path} ...")
    amenities = pd.read_csv(args.amenities_path)
    merged = mgr.merge_amenities(cleaned, amenities)
    print(f"      merged shape: {merged.shape}; matched amenity: {merged['amenity_score'].notna().sum()}")
    merged_path = args.output_dir / "listings_with_amenities.csv"
    merged.to_csv(merged_path, index=False)

    print("[4/8] Building preprocessor + splitting train/test ...")
    pre = build_preprocessor(NUMERIC_COLS, CATEGORICAL_COLS)
    feature_cols = NUMERIC_COLS + CATEGORICAL_COLS
    df = merged.dropna(subset=[TARGET]).copy()
    df = _prepare_features(df)
    df[feature_cols] = df[feature_cols].fillna({c: "missing" for c in CATEGORICAL_COLS})
    X = df[feature_cols]
    y = df[TARGET].astype(float)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=RANDOM_STATE
    )
    pre.fit(X_train)
    X_train_t = pre.transform(X_train)
    X_test_t = pre.transform(X_test)
    print(f"      train: {X_train_t.shape}, test: {X_test_t.shape}")

    print("[5/8] Cross-validating 4 models on train ...")
    metrics: dict = {
        "random_state": RANDOM_STATE,
        "test_size": args.test_size,
        "data_path": str(args.data_path),
        "models": {},
    }
    for name in ["dummy", "linear", "rf", "gbr"]:
        m = cv_metrics(
            X_train_t, y_train.values,
            model_name=name, log_target=True,
            n_splits=5, random_state=RANDOM_STATE,
        )
        pred = PricePredictor(model_name=name, log_target=True, random_state=RANDOM_STATE).fit(
            X_train_t, y_train.values
        )
        test_metrics = pred.evaluate(X_test_t, y_test.values)
        m["test_mae"] = test_metrics["mae"]
        m["test_rmse"] = test_metrics["rmse"]
        m["test_r2"] = test_metrics["r2"]
        metrics["models"][name] = m
        print(f"      {name:6s}: CV MAE={m['mae_mean']:.0f}±{m['mae_std']:.0f}, "
              f"Test MAE={test_metrics['mae']:.0f}, R²={test_metrics['r2']:.3f}")

    metrics_path = args.reports_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"      saved metrics → {metrics_path}")

    print("[6/8] Picking K by silhouette ...")
    best_k, scores = pick_k_by_silhouette(X_train_t, k_range=tuple(args.k_range), random_state=RANDOM_STATE)
    metrics["kmeans"] = {"best_k": best_k, "scores": {str(k): v for k, v in scores.items()}}
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"      best K={best_k} (silhouette scores: {scores})")

    print("[7/8] Fitting K-Means + assigning cluster to all listings ...")
    seg = KMeansSegmenter(n_clusters=best_k, random_state=RANDOM_STATE).fit(X_train_t)
    train_clusters = seg.predict(X_train_t)
    test_clusters = seg.predict(X_test_t)
    df_train = df.loc[X_train.index].copy()
    df_test = df.loc[X_test.index].copy()
    df_train["cluster"] = train_clusters
    df_test["cluster"] = test_clusters
    df_all_with_cluster = pd.concat([df_train, df_test], axis=0)
    df_all_with_cluster.to_csv(args.output_dir / "listings_with_clusters.csv", index=False)
    print(f"      cluster counts: {pd.Series(train_clusters.tolist() + test_clusters.tolist()).value_counts().to_dict()}")

    print("[8/8] Generating sample recommendations for 3 profiles ...")
    eng = RecommendationEngine()
    sample_profiles = [
        {
            "name": "Gia đình trẻ, 3 tỷ, Thủ Đức hoặc Bình Thạnh",
            "budget_vnd": 3e9,
            "target_bedrooms": 2,
            "target_area_m2": 65.0,
            "preferred_districts": ["Thành phố Thủ Đức", "Quận Bình Thạnh"],
            "preferred_cluster": 0,
        },
        {
            "name": "Nhà đầu tư, 5 tỷ, Quận 7 hoặc Bình Tân",
            "budget_vnd": 5e9,
            "target_bedrooms": 2,
            "target_area_m2": 70.0,
            "preferred_districts": ["Quận 7", "Quận Bình Tân"],
            "preferred_cluster": 1,
        },
        {
            "name": "Người mua cao cấp, 7 tỷ, Thủ Đức hoặc Quận 7",
            "budget_vnd": 7e9,
            "target_bedrooms": 3,
            "target_area_m2": 85.0,
            "preferred_districts": ["Thành phố Thủ Đức", "Quận 7"],
            "preferred_cluster": 2,
        },
    ]
    recs_out: list[pd.DataFrame] = []
    for prof in sample_profiles:
        recs = eng.recommend(
            df_all_with_cluster,
            budget_vnd=prof["budget_vnd"],
            target_bedrooms=prof["target_bedrooms"],
            target_area_m2=prof["target_area_m2"],
            preferred_districts=prof["preferred_districts"],
            preferred_cluster=prof["preferred_cluster"],
            top_k=5,
        )
        recs.insert(0, "profile", prof["name"])
        recs_out.append(recs)
    if recs_out:
        all_recs = pd.concat(recs_out, ignore_index=True)
    else:
        all_recs = pd.DataFrame()
    recs_path = args.reports_dir / "sample_recommendations.csv"
    all_recs.to_csv(recs_path, index=False)
    print(f"      saved → {recs_path} ({len(all_recs)} rows)")
    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
