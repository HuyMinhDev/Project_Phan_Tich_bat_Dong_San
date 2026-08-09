# Phân Tích & Gợi Ý Bất Động Sản Căn Hộ/Chung Cư TP.HCM (Chuyên Đề 3)

**Môn:** Lập trình cho Khoa học Dữ liệu
**Ngày cập nhật:** 2026-08-09
**Phạm vi:** Đồ án cuối kỳ — 1 thành viên

---

## Mục lục

- [Mô tả dự án](#mô-tả-dự-án)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Yêu cầu & Trạng thái](#yêu-cầu--trạng-thái)
- [Kiến trúc](#kiến-trúc)
- [Cài đặt](#cài-đặt)
- [Chạy lại toàn bộ pipeline](#chạy-lại-toàn-bộ-pipeline)
- [Kết quả](#kết-quả)
- [Phân công](#phân-công)
- [Giới hạn](#giới-hạn)

---

## Mô tả dự án

**Đề bài:** Phân tích dữ liệu tin đăng bất động sản căn hộ/chung cư tại 6 quận TP.HCM, dự đoán giá/m², phân cụm phân khúc thị trường và gợi ý top-5 căn hộ theo hồ sơ nhu cầu người dùng.

**Phạm vi dữ liệu:**

- Tin đăng căn hộ/chung cư 6 quận TP.HCM (Thủ Đức, Bình Thạnh, Quận 7, Gò Vấp, Quận 12, Bình Tân)
- Tiện ích theo phường/xã (trường học, bệnh viện, chợ, công viên, …)

**Mục tiêu:**

1. Chuẩn hóa dữ liệu thô (district, direction code, furnishing code, legal code, outlier)
2. Phân tích khám phá (EDA) — 11 biểu đồ (fig01–fig11, trong đó fig11 có 2 biểu đồ phụ)
3. Xây dựng mô hình dự đoán giá/m² (baseline + 3 supervised)
4. Phân cụm phân khúc (K-Means + silhouette auto-pick K)
5. Hệ gợi ý top-5 theo hồ sơ nhu cầu (hybrid filter)

---

## Cấu trúc thư mục

```
ChuoiKhoiUngDung/
├── data/
│   ├── raw/                                # Dữ liệu thô
│   │   ├── real_estate_apartment.xlsx             # 1799 tin BĐS căn hộ (1 nguồn chính)
│   │   ├── neighborhood_amenities.csv             # 91 phường/xã (tự tạo, nguồn phụ)
│   │   └── real_estate_house_old_backup.csv       # Backup nhà phố (không dùng cho ML)
│   ├── processed/                          # Dữ liệu sạch (CSV)
│   │   ├── listings_clean.csv                      # 1779 dòng (sau outlier filter)
│   │   ├── listings_with_amenities.csv             # 1779 dòng (đã merge tiện ích)
│   │   └── listings_with_clusters.csv              # 1779 dòng (có cluster_id, K=4)
│   └── logs/                               # Nhật ký xử lý
│       ├── cleaning_log.csv
│       └── error_log.txt
├── src/                                    # Mã nguồn Python (8 modules)
│   ├── domain.py                                # PropertyListing, Location (dataclass)
│   ├── cleaner.py                               # Quy tắc chuẩn hóa (decode hướng/nội thất/pháp lý)
│   ├── data_manager.py                          # PropertyDataManager (load CSV/XLSX + clean + merge + save)
│   ├── features.py                              # ColumnTransformer pipeline
│   ├── predictor.py                             # PricePredictor (Dummy + Linear + RF + GBR)
│   ├── segmenter.py                             # KMeansSegmenter (auto-pick K)
│   ├── recommender.py                           # RecommendationEngine (hybrid filter)
│   └── pipeline.py                              # CLI end-to-end
├── notebooks/
│   ├── 01_problem_and_data.ipynb           # Problem definition + data dictionary
│   ├── 02_collection_and_cleaning.ipynb    # Thu thập + cleaning + logs
│   ├── 03_eda.ipynb                        # EDA + 10 biểu đồ (fig01–fig10 + fig11_furnishing_legal)
│   └── 04_machine_learning.ipynb           # ML models + clustering (K=4) + reco 3 profiles
├── tests/                                  # 45 pytest tests (test_cleaner/data_manager/domain/features/predictor/recommender/segmenter)
├── reports/
│   ├── figures/                            # 12 PNG biểu đồ
│   ├── final_report.md                     # Báo cáo Markdown
│   ├── slide_outline.md                    # Slide thuyết trình
│   ├── metrics.json                        # MAE/RMSE/R² cho 4 model + silhouette scores
│   ├── sample_recommendations.csv          # Top-5 cho 3 hồ sơ nhu cầu
│   ├── data_dictionary.md
│   ├── ai_usage_log.md
│   └── member_contributions.md
├── scripts/
│   ├── make_neighborhood_amenities.py      # Tạo nguồn phụ từ xlsx
│   └── run_notebooks.py                    # Helper chạy 4 notebooks (nbclient headless)
├── requirements.txt
├── run_all.sh                              # Chạy tất cả (tests + pipeline + notebooks)
└── README.md
```

---

## Yêu cầu & Trạng thái

### A — Yêu cầu chung

| #   | Yêu cầu                   | Trạng thái | Ghi chú                                                               |
| --- | ------------------------- | ---------- | --------------------------------------------------------------------- |
| A1  | Quy trình KHDL đủ 9 bước  | ✅         | problem → collect → check → clean → EDA → viz → model → eval → report |
| A2  | Phạm vi hẹp, 2 tuần       | ✅         | 1 chuyên đề                                                           |
| A3  | Không vi phạm pháp lý     | ✅         | Dữ liệu tổng hợp, không crawl web thật                                |
| A4  | Phương án dự phòng        | ✅         | Fallback khi thiếu amenities                                          |
| A5  | ≥2 nguồn/định dạng        | ✅         | 1 xlsx + 1 CSV (listings + amenities)                                 |
| A6  | ≥1.000 bản ghi            | ✅         | 1799 listings (raw) → 1779 sau outlier filter                         |
| A7  | ≥10 thuộc tính            | ✅         | 41 cột sau khi load + chuẩn hóa                                       |
| A8  | Có dữ liệu bẩn            | ✅         | Direction thiếu 79%, area ngoài phạm vi, giá outlier                  |
| A9  | Baseline                  | ✅         | DummyRegressor (median)                                               |
| A10 | ≥2 mô hình có giám sát    | ✅         | Linear Regression, Random Forest, Gradient Boosting                   |
| A11 | 1 bài toán phân cụm/gợi ý | ✅         | K-Means (K=4) + Hybrid Recommendation                                 |
| A12 | Chia train/test           | ✅         | 80/20 split, random_state=42                                          |
| A13 | Dùng Pipeline             | ✅         | ColumnTransformer (numeric + categorical)                             |
| A14 | Không đánh giá trên train | ✅         | 5-fold CV + test riêng                                                |
| A15 | ≥10 trường hợp sai        | ✅         | Top-10 worst predictions trong notebook 04 (Cell 8)                   |
| A16 | Nêu giới hạn dữ liệu     | ✅         | Section "Giới hạn" cuối README + report                               |
| A17 | ≥8 biểu đồ                | ✅         | 12 file PNG trong `reports/figures/` (10 EDA + 2 cell 11)             |

### B — Sản phẩm bắt buộc

| #   | Yêu cầu        | File                                           | Status                          |
| --- | -------------- | ---------------------------------------------- | ------------------------------- |
| B1  | Notebook 1     | `notebooks/01_problem_and_data.ipynb`          | ✅ Executed                     |
| B2  | Notebook 2     | `notebooks/02_collection_and_cleaning.ipynb`   | ✅ Executed                     |
| B3  | Notebook 3     | `notebooks/03_eda.ipynb`                       | ✅ 10 biểu đồ EDA chính         |
| B4  | Notebook 4     | `notebooks/04_machine_learning.ipynb`          | ✅ 4 models + clustering + reco |
| B5  | Mã nguồn `src/`| `src/` (8 files)                               | ✅                              |
| B6  | Dữ liệu gốc    | `data/raw/`                                    | ✅ 1 xlsx + 1 CSV               |
| B7  | Dữ liệu sạch   | `data/processed/`                              | ✅ 3 CSV                        |
| B8  | Nhật ký lỗi    | `data/logs/cleaning_log.csv` + `error_log.txt` | ✅                              |
| B9  | Báo cáo        | `reports/final_report.md` + `slide_outline.md` | ✅                              |
| B10 | README         | `README.md`                                    | ✅ (file này)                   |
| B11 | AI usage log   | `reports/ai_usage_log.md`                      | ✅                              |
| B12 | Bảng phân công | `reports/member_contributions.md`              | ✅                              |

### C — Yêu cầu dữ liệu

| #   | Yêu cầu                   | Trạng thái                                                         |
| --- | ------------------------- | ------------------------------------------------------------------ |
| C1  | Tin BĐS căn hộ TP.HCM     | ✅ 1799 records (raw) → 1779 (sau outlier filter)                   |
| C2  | Cấu trúc `PropertyListing`| ✅ Dataclass 19 fields                                             |
| C3  | Cấu trúc `Location`       | ✅ district, ward, amenity_score                                   |
| C4  | ≥1.000 tin                | ✅ 1779                                                            |
| C5  | ≥10 thuộc tính            | ✅ 41 cột sau load + chuẩn hóa                                     |
| C6  | ≥2 quận                   | ✅ 6 quận (Thủ Đức, Bình Thạnh, Quận 7, Gò Vấp, Quận 12, Bình Tân) |
| C7  | 2+ nguồn                  | ✅ XLSX + CSV                                                      |

### D — Yêu cầu OOP & Python

| #   | Yêu cầu                | File                  | Status                                    |
| --- | ---------------------- | --------------------- | ----------------------------------------- |
| D1  | `PropertyListing`      | `src/domain.py`       | ✅ Dataclass, 19 fields                   |
| D2  | `Location`             | `src/domain.py`       | ✅ Dataclass + property                   |
| D3  | `PropertyDataManager`  | `src/data_manager.py` | ✅ Load (CSV/XLSX) + clean + merge + save |
| D4  | `RecommendationEngine` | `src/recommender.py`  | ✅ Hybrid filter + scoring                |
| D5  | Đọc nhiều format       | `src/data_manager.py` | ✅ CSV + XLSX                             |
| D6  | Xử lý missing          | `src/cleaner.py`      | ✅ IQR filter + imputation                |
| D7  | Ghi lỗi + metadata     | `src/data_manager.py` | ✅ cleaning_log + error_log               |

### E — Yêu cầu làm sạch

| #   | Yêu cầu                 | Xử lý                                        | Status |
| --- | ----------------------- | -------------------------------------------- | ------ |
| E1  | Chuẩn hóa quận/huyện    | Pass-through (data đã chuẩn)                 | ✅     |
| E2  | Chuẩn hóa hướng nhà     | Decode mã 1..8 → 8 hướng chính               | ✅     |
| E3  | Chuẩn hóa nội thất      | Decode mã 1..4 → nhãn tiếng Việt             | ✅     |
| E4  | Chuẩn hóa pháp lý       | Decode mã 1,2,4,5,6 → nhãn tiếng Việt        | ✅     |
| E5  | Xử lý outlier giá       | Filter < 100 triệu / > 500 triệu / m²        | ✅     |
| E6  | Xử lý outlier diện tích | Filter < 10 hoặc > 500 m²                    | ✅     |
| E7  | Xử lý outlier phòng     | Filter > 10 phòng                            | ✅     |
| E8  | Xử lý thiếu             | NaN giữ nguyên, impute median trong Pipeline | ✅     |
| E9  | Xử lý trùng             | Exact (listing_id)                           | ✅     |
| E10 | Xử lý sai kiểu          | Coerce numeric, validate area_m2 > 0         | ✅     |

### F — Câu hỏi nghiên cứu

| #   | Câu hỏi                             | Notebook | Trạng thái           |
| --- | ----------------------------------- | -------- | -------------------- |
| F1  | Quận nào có giá/m² cao nhất?        | 03_eda   | ✅ Top 6 quận        |
| F2  | Diện tích/phòng ảnh hưởng thế nào?  | 03_eda   | ✅ Scatter + boxplot |
| F3  | Hướng/nội thất/pháp lý liên hệ giá? | 03_eda   | ✅ Boxplot + heatmap |
| F4  | Số tin đăng theo quận?              | 03_eda   | ✅ Bar chart         |
| F5  | Mô hình dự đoán sai số bao nhiêu?   | 04_ml    | ✅ RMSE, MAE, R²     |
| F6  | Bao nhiêu phân khúc thị trường?     | 04_ml    | ✅ K-Means K=4       |
| F7  | Top-5 BĐS phù hợp với từng hồ sơ?   | 04_ml    | ✅ Hybrid filter     |

### G — Yêu cầu mô hình

| #   | Yêu cầu               | File                 | Status                                                         |
| --- | --------------------- | -------------------- | -------------------------------------------------------------- |
| G1  | Baseline              | `src/predictor.py`   | ✅ DummyRegressor (median), Test R² = -0.041                   |
| G2  | Linear Regression     | `src/predictor.py`   | ✅ log-target, Test R² = 0.143, CV R² = 0.294                  |
| G3  | Random Forest         | `src/predictor.py`   | ✅ n_estimators=200, **Test R² = 0.169** (best), CV R² = 0.357 |
| G4  | Gradient Boosting     | `src/predictor.py`   | ✅ n_estimators=200, Test R² = 0.162, CV R² = 0.366           |
| G5  | K-Means clustering    | `src/segmenter.py`   | ✅ auto-pick K=4 (silhouette=0.083)                            |
| G6  | Hybrid recommendation | `src/recommender.py` | ✅ Hybrid filter (district + price + area + cluster + amenity) |

### H — Yêu cầu EDA & Trực quan

| #   | Yêu cầu              | Status                                                        |
| --- | -------------------- | ------------------------------------------------------------- |
| H1  | ≥8 biểu đồ           | ✅ 12 file PNG (fig01–fig10 + 2 biểu đồ fig11)                |
| H2  | Groupby/Pivot        | ✅ Pivot district × price_band                                |
| H3  | 5 bảng Groupby/Pivot | ✅ District, direction, bedrooms, furnishing, legal           |

### J — Điều kiện đạt

| #   | Điều kiện                          | Status                                          |
| --- | ---------------------------------- | ----------------------------------------------- |
| J1  | Có dữ liệu gốc và đã làm sạch      | ✅ 1799 raw → 1779 cleaned                      |
| J2  | Mã nguồn chạy được từ đầu đến cuối | ✅ `bash run_all.sh` → tất cả notebooks OK      |
| J3  | Có baseline và đánh giá trên test  | ✅ Baseline + 3 models + 5-fold CV               |
| J4  | Phân công và minh chứng            | ✅ `reports/member_contributions.md`            |
| J5  | Giải thích được kết quả AI         | ✅ `reports/ai_usage_log.md`                     |
| J6  | Không vi phạm quyền riêng tư       | ✅ 100% dữ liệu tổng hợp, không PII            |

---

## Kiến trúc

### Quy trình xử lý (Pipeline)

```
data/raw/real_estate_apartment.xlsx (1799 tin BĐS căn hộ)
                ↓
        [cleaner.py] — chuẩn hóa district + direction
        [cleaner.py] — decode furnishing + legal (mã 1..6 → nhãn VN)
        [cleaner.py] — outlier filter (area 10–500, price 100–500tr/m², BR ≤ 10)
                ↓
data/processed/listings_clean.csv (1779 dòng, 41 cột)
                ↓
        [data_manager.py] — merge amenities theo (district_clean, ward)
        [data_manager.py] — fill missing amenities = median theo district
                ↓
data/processed/listings_with_amenities.csv (1779 dòng, ~44 cột)
                ↓
        [features.py] — ColumnTransformer (numeric + categorical)
                ↓
        [predictor.py] — 4 models (Dummy/Linear/RF/GBR) + 5-fold CV + test evaluation
        [segmenter.py] — K-Means + silhouette auto-pick K (K=4)
                ↓
data/processed/listings_with_clusters.csv (1779 dòng, +cluster_id)
                ↓
        [recommender.py] — top-5 cho 3 hồ sơ nhu cầu mẫu
                ↓
reports/sample_recommendations.csv + reports/metrics.json
```

### ER Diagram (đơn giản)

```
+--------------------+         +-------------------------+
| neighborhood_      |         |  listings_clean.csv     |
| amenities.csv      |         |-------------------------|
|--------------------|         | listing_id (PK)         |
| district_clean     |-------->| district_clean          |
| ward               |         | ward                    |
| amenity_score      |         | area_m2                 |
| school_count       |         | bedrooms                |
| hospital_count     |         | total_price             |
| supermarket_count  |         | price_per_m2            |
| park_count         |         | direction_code          |
| bus_stops_count    |         | furnishing_code         |
+--------------------+         | legal_code              |
                               | project_name            |
                               | apartment_type          |
                               | ... (32 cột gốc + 9 cột chuẩn hóa) |
                               +-------------------------+
                                       |
                                       | K-Means (K=4)
                                       ↓
                               +-------------------------+
                               | listings_with_clusters  |
                               | cluster_id (K=4)        |
                               +-------------------------+
```

### ML Pipeline

```
Clean Data (1779 rows × 41 cols)
    ↓
ColumnTransformer (impute median + scale + OHE categorical)
    ↓
12 features được transform (9 numeric + 3 categorical OHE)
    ↓
Baseline (DummyRegressor, log-target)
    ↓
Linear Regression (log-target)
    ↓
Random Forest (n_estimators=200, max_depth=None, min_samples_leaf=2)
    ↓
Gradient Boosting (n_estimators=200, max_depth=4, learning_rate=0.05)
    ↓
Evaluation: MAE, RMSE, R² (5-fold CV trên train + test set 355 mẫu)
    ↓
Error Analysis (top-10 worst predictions — Cell 8 notebook 04)

Unsupervised:
    Features (47-dim) → StandardScaler → K-Means (K ∈ {3,4,5,6})
    ↓
    silhouette score → best K=4 (0.083)
    ↓
Cluster profiles (1396 / 165 / 165 / 47 tin theo cluster 1/0/3/2)

Recommendation (hybrid):
    Listings + User profile → hard filter (district + price ±20% + BR ±1)
    ↓
    Score = price_score + area_score + cluster_bonus (0.3) + amenity_bonus (0.2)
    ↓
    Top-5 theo score_total giảm dần
```

---

## Cài đặt

```bash
# Clone repo (hoặc vào thư mục dự án)
cd src/ChuoiKhoiUngDung

# Cài dependencies chính
python3 -m pip install -r requirements.txt

# Cài thêm để chạy notebook tự động (headless)
python3 -m pip install nbformat nbclient ipykernel openpyxl
```

### requirements.txt

```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
scikit-learn>=1.3.0
pytest>=7.4.0
openpyxl>=3.0.0
```

---

## Chạy lại toàn bộ pipeline

### Cách 1 — Một lệnh duy nhất (khuyến nghị)

```bash
cd src/ChuoiKhoiUngDung
bash run_all.sh
```

Script này tự động:

1. Chạy 45 unit tests (`pytest tests/ -q` → 45/45 PASS)
2. Chạy pipeline end-to-end (`python3 -m src.pipeline`)
3. Chạy cả 4 notebooks headless (lưu `*_executed.ipynb`)
4. Sinh toàn bộ output vào `reports/` + `data/processed/`

⏱️ Tổng thời gian: ~25–30 giây.

### Cách 2 — Chạy từng phần

**1. Tạo nguồn dữ liệu thứ 2 (nếu chưa có):**

```bash
python3 -m scripts.make_neighborhood_amenities
```

**2. Chạy tests:**

```bash
python3 -m pytest tests/ -v
# Mong đợi: 45 passed
```

**3. Chạy pipeline end-to-end:**

```bash
python3 -m src.pipeline
```

Output:

- `data/processed/listings_clean.csv`
- `data/processed/listings_with_amenities.csv`
- `data/processed/listings_with_clusters.csv`
- `reports/metrics.json`
- `reports/sample_recommendations.csv`

**4. Chạy notebooks (headless, qua nbclient):**

```bash
PYTHONPATH=. python3 scripts/run_notebooks.py
```

**5. Chạy notebooks (Jupyter UI):**

```bash
jupyter notebook notebooks/
# Mở lần lượt 01 → 02 → 03 → 04, nhấn "Run All Cells"
```

### Output files

| File                                          | Mô tả                              |
| --------------------------------------------- | ---------------------------------- |
| `data/processed/listings_clean.csv`           | Dữ liệu đã chuẩn hóa (1779 dòng)   |
| `data/processed/listings_with_amenities.csv`  | Merge tiện ích theo phường         |
| `data/processed/listings_with_clusters.csv`   | Có cluster_id (K=4)                |
| `reports/metrics.json`                        | MAE/RMSE/R² + silhouette scores    |
| `reports/sample_recommendations.csv`          | Top-5 cho 3 user profiles          |
| `reports/figures/fig01–fig11*.png`            | 12 file PNG (10 EDA + 2 cell 11)   |
| `data/logs/cleaning_log.csv`                  | Nhật ký từng bước làm sạch         |
| `data/logs/error_log.txt`                     | Lỗi phát hiện trong quá trình      |

---

## Kết quả

### Data

| Chỉ tiêu                   | Giá trị         |
| -------------------------- | --------------- |
| Tổng số tin (raw)          | 1799            |
| Thuộc tính sau load        | 41 cột          |
| Quận/huyện                 | 6 quận TP.HCM   |
| Phường/xã có amenities     | 91              |
| Records sau outlier filter | 1779            |
| Coverage amenities         | ~99% (merge theo district + ward) |

### 6 quận trong dữ liệu (số tin đã clean)

| Quận                | Số tin | Ghi chú                  |
| ------------------- | -----: | ------------------------ |
| Thành phố Thủ Đức   | 597    | Quận mới sáp nhập 2021   |
| Quận 7              | 354    | Khu Nam Sài Gòn          |
| Quận Bình Tân       | 302    | Ngoại thành Tây          |
| Quận Bình Thạnh     | 212    | Ven sông Sài Gòn         |
| Quận 12             | 173    | Ngoại thành Bắc          |
| Quận Gò Vấp         | 141    | Ngoại thành Bắc          |
| **Tổng**            | **1779** |                          |

### Models (target = price_per_m2, VND, log-target)

| Model                   | CV MAE   | CV R² | Test MAE  | Test RMSE | Test R² |
| ----------------------- | --------:| -----:| ---------:| ---------:| -------:|
| Baseline (Dummy median) | 18.8M    | -0.048| 18.5M     | 37.1M     | -0.041  |
| Linear Regression       | 14.1M    | 0.294 | 14.9M     | 33.7M     |  0.143  |
| **Random Forest**       | **13.0M**| **0.357**| **13.9M** | **33.2M** | **0.169** |
| Gradient Boosting       | 13.4M    | 0.366 | 14.4M     | 33.7M     |  0.162  |

> **Best model:** Random Forest — Test R² = 0.169, RMSE ≈ 33.2 triệu VND/m², MAE ≈ 13.9 triệu VND/m² (~26% sai số so với median 53tr/m²).
>
> **Overfitting nhẹ (CV R² > Test R²):** Gap CV-Test của RF là 0.188 (nhỏ nhất trong 4 model) → RF generalize tốt nhất. GBR có CV R² = 0.366 nhỉnh hơn RF nhưng gap = 0.204 → RF vẫn được chọn.

### Clustering (K-Means, auto-pick bằng silhouette)

| K     | Silhouette | Chọn?     |
| ----- | ---------- | --------- |
| 3     | 0.079      | —         |
| **4** | **0.083**  | ✅ (best) |
| 5     | 0.027      | —         |
| 6     | -0.061     | —         |

> **K=4** được chọn tự động. Phân bố cluster (sau khi predict toàn bộ 1779 tin):
>
> | Cluster | Số tin | Tỷ lệ  | Đặc điểm                                              |
> | -------:| ------:| ------:| ------------------------------------------------------ |
> | 0       | 165    | 9.3%   | Căn hộ diện tích nhỏ, view Đông/Tây Nam               |
> | **1**   | **1396** | **78.5%** | **Đa số — căn hộ tiêu chuẩn (2PN, 60–80m²)**     |
> | 2       | 47     | 2.6%   | Căn hộ nhỏ ở Thủ Đức (chỉ district này)              |
> | 3       | 165    | 9.3%   | Căn hộ hướng Tây/Tây Bắc (đặc trưng)                |
>
> Silhouette thấp (0.083) → các cụm tách biệt không rõ; giá median giữa các cluster gần như nhau (~50–54tr/m²) → model chưa phân biệt rõ phân khúc giá.

### Recommendation (top-5 cho 3 hồ sơ căn hộ)

3 hồ sơ nhu cầu mẫu (dùng district **thực tế có trong data**):

1. **Gia đình trẻ, 3 tỷ, Thủ Đức / Bình Thạnh** — 2PN, 65m², cluster 0
2. **Nhà đầu tư, 5 tỷ, Quận 7 / Bình Tân** — 2PN, 70m², cluster 1
3. **Người mua cao cấp, 7 tỷ, Thủ Đức / Quận 7** — 3PN, 85m², cluster 1

> **Lưu ý quan trọng:**
> - `preferred_cluster` chỉ là **bonus điểm (+0.3)** chứ không phải hard filter. Profile cao cấp 7 tỷ ban đầu dùng cluster 2 (chỉ 47 tin ở Thủ Đức, giá 1.58–4.6 tỷ) → 0 tin khớp filter cứng → đã đổi sang cluster 1.
> - District name phải khớp **chính xác** với data (Thành phố Thủ Đức, Quận 7, Quận Bình Thạnh, Quận Bình Tân, Quận 12, Quận Gò Vấp). Sai tên → recommend trả về rỗng.

Cả 3 hồ sơ đều có kết quả top-5. Xem chi tiết trong `reports/sample_recommendations.csv`.

---

## Phân công

Đồ án đóng gói 1 thành viên. Chi tiết tại `reports/member_contributions.md`.

| Trục   | Nhiệm vụ chính                                                  | Hoàn thành |
| ------ | --------------------------------------------------------------- | ---------- |
| Data   | Setup dự án + requirements + README                             | ✅         |
| Data   | Tạo `neighborhood_amenities.csv`                                | ✅         |
| Data   | Domain classes (`PropertyListing`, `Location`)                  | ✅         |
| Data   | Cleaner: district + direction + decode                          | ✅         |
| Data   | `PropertyDataManager`: load (CSV/XLSX) + clean + merge + save   | ✅         |
| Data   | Feature pipeline (`ColumnTransformer`)                          | ✅         |
| Model  | `PricePredictor`: Dummy + Linear + RF + GBR + CV                | ✅         |
| Model  | `KMeansSegmenter` + silhouette auto-pick K                      | ✅         |
| Model  | `RecommendationEngine`: hybrid filter + scoring                 | ✅         |
| Model  | Pipeline CLI end-to-end                                         | ✅         |
| Cả hai | 4 notebooks + báo cáo + slide + dictionary + AI log             | ✅         |

**Kiểm tra chéo:** 45 pytest tests (`pytest tests/ -v` → **45/45 PASS**).

**Trình bày:** Tối thiểu 7 phút × 1 người = 7 phút + Q&A.

---

## Giới hạn (A16)

1. **Phạm vi 6 quận** — không có Quận 1, 3, 4, 5 (trung tâm) → bias về khu vực và tier giá. Trung tâm TP.HCM (Quận 1, 3) có giá/m² thường > 150tr sẽ không được đại diện.
2. **Dữ liệu tổng hợp từ 1 nguồn (chotot)** — chưa phản ánh đầy đủ thị trường (batdongsan.com.vn, alonhadat.com.vn, mogi.vn…).
3. **R² thấp (0.17)** — giá căn hộ phụ thuộc nhiều yếu tố phi số (view sông, tầng cao, nội thất chi tiết, tiến độ dự án, chính sách trả góp) không có trong data → sai số ~25–26% so với median.
4. **Silhouette thấp (0.083)** — K-Means khó tách rõ phân khúc vì features hạn chế; các cluster phân biệt chủ yếu theo direction/diện tích, KHÔNG theo phân khúc giá (median giá gần như nhau giữa 4 cluster).
5. **Cluster mất cân đối** — cluster 1 chiếm 78.5% (1396/1779 tin), cluster 2 chỉ 2.6% (47 tin) → bonus cluster không hiệu quả cho các cluster nhỏ.
6. **Missing cao** — direction 79%, balcony_direction 73%, furnishing 34% → impute median có thể bias.
7. **Recommendation đơn giản** — chỉ dùng rule-based scoring (price + area + cluster + amenity), chưa có collaborative filtering hay matrix factorization.
8. **Thiếu temporal** — không xét biến động giá theo thời gian (chỉ có `posted_at`).
9. **Không có text mining** — bỏ qua `description` và `title` (có thể chứa thông tin "view sông", "tầng X", "gần metro").

---

## AI Usage

Xem `reports/ai_usage_log.md` — ghi lại prompt, đầu ra AI, cách kiểm chứng và chỉnh sửa của dự án.
