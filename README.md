# Phân Tích & Gợi Ý Bất Động Sản Nhà Phố TP.HCM (Chuyên Đề 3)

**Môn:** Lập trình cho Khoa học Dữ liệu
**Ngày:** 2026-07-23
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

**Đề bài:** Phân tích dữ liệu tin đăng bất động sản nhà phố tại TP.HCM, dự đoán giá/m², phân cụm phân khúc thị trường và gợi ý top-5 bất động sản theo hồ sơ nhu cầu người dùng.

**Phạm vi dữ liệu:**
- Tin đăng nhà phố TP.HCM (quận, hướng, diện tích, phòng ngủ, giá, ngày đăng, …)
- Tiện ích theo phường/xã (trường học, bệnh viện, chợ, công viên, …)

**Mục tiêu:**
1. Chuẩn hóa dữ liệu thô (district, direction, outlier)
2. Phân tích khám phá (EDA) — 10 biểu đồ
3. Xây dựng mô hình dự đoán giá/m² (baseline + 3 supervised)
4. Phân cụm phân khúc (K-Means + silhouette auto-pick K)
5. Hệ gợi ý top-5 theo hồ sơ nhu cầu (hybrid filter)

---

## Cấu trúc thư mục

```
ChuoiKhoiUngDung/
├── data/
│   ├── raw/                                # Dữ liệu thô (CSV)
│   │   ├── real_estate_with_price_per_m2.csv        # 3.000 tin BĐS
│   │   └── neighborhood_amenities.csv              # 100 phường/xã
│   ├── processed/                          # Dữ liệu sạch (CSV)
│   │   ├── listings_clean.csv
│   │   ├── listings_with_amenities.csv
│   │   └── listings_with_clusters.csv
│   └── logs/                               # Nhật ký xử lý
│       ├── cleaning_log.csv
│       └── error_log.txt
├── src/
│   ├── domain.py                           # PropertyListing, Location
│   ├── cleaner.py                          # Quy tắc chuẩn hóa
│   ├── data_manager.py                     # PropertyDataManager (load+clean+merge+save)
│   ├── features.py                         # ColumnTransformer pipeline
│   ├── predictor.py                        # PricePredictor (Dummy + Linear + RF + GBR)
│   ├── segmenter.py                        # KMeansSegmenter (auto-pick K)
│   ├── recommender.py                      # RecommendationEngine (hybrid filter)
│   └── pipeline.py                         # CLI end-to-end
├── notebooks/
│   ├── 01_problem_and_data.ipynb           # Problem definition + data dictionary
│   ├── 02_collection_and_cleaning.ipynb    # Thu thập + cleaning + logs
│   ├── 03_eda.ipynb                        # EDA + 10 biểu đồ
│   └── 04_machine_learning.ipynb           # ML models + clustering + reco demo
├── tests/                                  # 35 pytest tests
├── reports/
│   ├── figures/                            # 11 PNG biểu đồ
│   ├── final_report.md                     # Báo cáo Markdown
│   ├── slide_outline.md                    # Slide thuyết trình
│   ├── metrics.json                        # MAE/RMSE/R² cho 4 model + silhouette
│   ├── sample_recommendations.csv          # Top-5 cho 3 hồ sơ nhu cầu
│   ├── data_dictionary.md
│   ├── ai_usage_log.md
│   └── member_contributions.md
├── scripts/
│   └── make_neighborhood_amenities.py      # Tạo nguồn phụ
├── requirements.txt
├── run_all.sh                              # Chạy tất cả (tests + pipeline + notebooks)
└── README.md
```

---

## Yêu cầu & Trạng thái

### A — Yêu cầu chung

| #  | Yêu cầu | Trạng thái | Ghi chú |
|----|---------|------------|---------|
| A1 | Quy trình KHDL đủ 9 bước | ✅ | problem → collect → check → clean → EDA → viz → model → eval → report |
| A2 | Phạm vi hẹp, 2 tuần | ✅ | 1 chuyên đề |
| A3 | Không vi phạm pháp lý | ✅ | Dữ liệu tổng hợp, không crawl web thật |
| A4 | Phương án dự phòng | ✅ | Fallback khi thiếu amenities |
| A5 | ≥2 nguồn/định dạng | ✅ | 2 CSV (listings + amenities) |
| A6 | ≥1.000 bản ghi | ✅ | 3.000 listings |
| A7 | ≥10 thuộc tính | ✅ | 13 columns trong PropertyListing |
| A8 | Có dữ liệu bẩn | ✅ | District typo, direction lộn xộn, outlier giá |
| A9 | Baseline | ✅ | DummyRegressor (mean) |
| A10 | ≥2 mô hình có giám sát | ✅ | Linear Regression, Random Forest, Gradient Boosting |
| A11 | 1 bài toán phân cụm/gợi ý | ✅ | K-Means + Content-based Recommendation |
| A12 | Chia train/test | ✅ | 80/20 split, random_state=42 |
| A13 | Dùng Pipeline | ✅ | ColumnTransformer (numeric + categorical) |
| A14 | Không đánh giá trên train | ✅ | 5-fold CV + test riêng |
| A15 | ≥10 trường hợp sai | ✅ | Error analysis trong notebook 04 |
| A16 | Nêu giới hạn dữ liệu | ✅ | Section cuối README + report |
| A17 | ≥8 biểu đồ | ✅ | 10 biểu đồ trong `03_eda` |

### B — Sản phẩm bắt buộc

| #  | Yêu cầu | File | Status |
|----|---------|------|--------|
| B1 | Notebook 1 | `notebooks/01_problem_and_data.ipynb` | ✅ Executed |
| B2 | Notebook 2 | `notebooks/02_collection_and_cleaning.ipynb` | ✅ Executed |
| B3 | Notebook 3 | `notebooks/03_eda.ipynb` | ✅ 10 charts |
| B4 | Notebook 4 | `notebooks/04_machine_learning.ipynb` | ✅ 4 models + clustering + reco |
| B5 | Mã nguồn `src/` | `src/` (8 files) | ✅ |
| B6 | Dữ liệu gốc | `data/raw/` | ✅ 2 CSV |
| B7 | Dữ liệu sạch | `data/processed/` | ✅ 3 CSV |
| B8 | Nhật ký lỗi | `data/logs/cleaning_log.csv` + `error_log.txt` | ✅ |
| B9 | Báo cáo | `reports/final_report.md` + `slide_outline.md` | ✅ |
| B10 | README | `README.md` | ✅ |
| B11 | AI usage log | `reports/ai_usage_log.md` | ✅ |
| B12 | Bảng phân công | `reports/member_contributions.md` | ✅ |

### C — Yêu cầu dữ liệu

| #  | Yêu cầu | Trạng thái |
|----|---------|------------|
| C1 | Tin BĐS nhà phố TP.HCM | ✅ 3.000 records |
| C2 | Cấu trúc `PropertyListing` | ✅ 13 fields |
| C3 | Cấu trúc `Location` | ✅ district, ward, amenity_score |
| C4 | ≥1.000 tin | ✅ 3.000 |
| C5 | ≥10 thuộc tính | ✅ 13 |
| C6 | ≥2 quận | ✅ 24 quận/huyện TP.HCM |
| C7 | 2+ nguồn | ✅ Listings + Amenities |

### D — Yêu cầu OOP & Python

| #  | Yêu cầu | File | Status |
|----|---------|------|--------|
| D1 | `PropertyListing` | `src/domain.py` | ✅ Dataclass, 13 fields |
| D2 | `Location` | `src/domain.py` | ✅ Dataclass + property |
| D3 | `PropertyDataManager` | `src/data_manager.py` | ✅ Load + clean + merge + save |
| D4 | `RecommendationEngine` | `src/recommender.py` | ✅ Hybrid filter + scoring |
| D5 | Đọc CSV | `src/data_manager.py` | ✅ pandas.read_csv |
| D6 | Phát hiện trùng | `src/cleaner.py` | ✅ Exact dedup |
| D7 | Ghi lỗi + metadata | `src/data_manager.py` | ✅ cleaning_log + error_log |

### E — Yêu cầu làm sạch

| #  | Yêu cầu | Xử lý | Status |
|----|---------|-------|--------|
| E1 | Chuẩn hóa quận/huyện | Số → tên đầy đủ (Quận 1, Quan 1 → "Quận 1") | ✅ |
| E2 | Chuẩn hóa hướng nhà | Map variants → 8 hướng chuẩn | ✅ |
| E3 | Chuẩn hóa loại BĐS | Map variants → 5 loại | ✅ |
| E4 | Xử lý outlier giá | IQR filter | ✅ |
| E5 | Xử lý thiếu | NaN giữ nguyên, báo cáo tỷ lệ | ✅ |
| E6 | Xử lý trùng | Exact (listing_id) | ✅ |
| E7 | Xử lý sai kiểu | Coerce numeric, validate area_m2 > 0 | ✅ |

### F — Câu hỏi nghiên cứu

| #  | Câu hỏi | Notebook | Trạng thái |
|----|---------|----------|------------|
| F1 | Quận nào có nhiều tin nhất? | 03_eda | ✅ Top-10 districts |
| F2 | Giá/m² thay đổi theo quận, hướng, diện tích? | 03_eda | ✅ Boxplot + scatter + heatmap |
| F3 | Diện tích ảnh hưởng đến giá thế nào? | 03_eda | ✅ Scatter area × price |
| F4 | Số phòng ngủ phân bố ra sao? | 03_eda | ✅ Bar chart |
| F5 | Mô hình dự đoán sai số bao nhiêu? | 04_ml | ✅ RMSE, MAE, R² + error analysis |
| F6 | Bao nhiêu phân khúc thị trường? | 04_ml | ✅ K-Means + silhouette |
| F7 | Top-5 BĐS phù hợp với từng hồ sơ? | 04_ml | ✅ Hybrid filter, top-5 |

### G — Yêu cầu mô hình

| #  | Yêu cầu | File | Status |
|----|---------|------|--------|
| G1 | Baseline | `src/predictor.py` | ✅ DummyRegressor (mean) |
| G2 | Linear Regression | `src/predictor.py` | ✅ log-target, RMSE=126.5M, R²=0.285 |
| G3 | Random Forest | `src/predictor.py` | ✅ n_estimators=200, RMSE=117.1M, R²=0.388 |
| G4 | Gradient Boosting | `src/predictor.py` | ✅ n_estimators=200, RMSE=118.8M, R²=0.369 |
| G5 | K-Means clustering | `src/segmenter.py` | ✅ auto-pick K=3 (silhouette=0.087) |
| G6 | Content-based reco | `src/recommender.py` | ✅ Hybrid filter (location + price + area) |

### H — Yêu cầu EDA & Trực quan

| #  | Yêu cầu | Status |
|----|---------|--------|
| H1 | ≥8 biểu đồ | ✅ 10 biểu đồ (fig01–fig10) + silhouette (fig11) |
| H2 | Groupby/Pivot | ✅ Pivot district × price_band |
| H3 | 5 bảng Groupby/Pivot | ✅ District, direction, bedrooms, area_bin, amenity |

### J — Điều kiện đạt

| #  | Điều kiện | Status |
|----|-----------|--------|
| J1 | Có dữ liệu gốc và đã làm sạch | ✅ 3.000 listings → 3 processed CSV |
| J2 | Mã nguồn chạy được từ đầu đến cuối | ✅ `bash run_all.sh` → DONE |
| J3 | Có baseline và đánh giá trên test | ✅ Baseline + 3 models + 5-fold CV |
| J4 | Phân công và minh chứng | ✅ `member_contributions.md` |
| J5 | Giải thích được kết quả AI | ✅ `ai_usage_log.md` |
| J6 | Không vi phạm quyền riêng tư | ✅ 100% dữ liệu tổng hợp, không PII |

---

## Kiến trúc

### Quy trình xử lý (Pipeline)

```
data/raw/real_estate_with_price_per_m2.csv (3.000 tin)
                ↓
        [cleaner.py] — chuẩn hóa district + direction + property_type
        [cleaner.py] — IQR outlier filter
                ↓
data/processed/listings_clean.csv
                ↓
        [data_manager.py] — merge amenities theo ward
                ↓
data/processed/listings_with_amenities.csv
                ↓
        [features.py] — ColumnTransformer (numeric + categorical)
                ↓
        [predictor.py] — 4 models + 5-fold CV + test evaluation
        [segmenter.py] — K-Means + silhouette auto-pick K
                ↓
data/processed/listings_with_clusters.csv
                ↓
        [recommender.py] — top-5 cho 3 hồ sơ nhu cầu mẫu
                ↓
reports/sample_recommendations.csv + reports/metrics.json
```

### ER Diagram (đơn giản)

```
+-------------------+         +-------------------------+
| neighborhood_     |         |  listings_clean.csv     |
| amenities.csv     |         |-------------------------|
|-------------------|         | listing_id (PK)         |
| district          |-------->| district_clean          |
| ward              |         | ward                    |
| amenity_score     |         | area_m2                 |
| school_count      |         | bedrooms                |
| hospital_count    |         | total_price             |
| market_count      |         | price_per_m2            |
| park_count        |         | house_direction         |
+-------------------+         | property_type           |
                              +-------------------------+
                                       |
                                       | K-Means
                                       ↓
                              +-------------------------+
                              | listings_with_clusters  |
                              | cluster_id (K=3)       |
                              +-------------------------+
```

### ML Pipeline

```
Clean Data → ColumnTransformer (impute + scale + OHE)
    ↓
Baseline (DummyRegressor, log-target)
    ↓
Linear Regression (log-target)
    ↓
Random Forest (n_estimators=200, max_depth=12)
    ↓
Gradient Boosting (n_estimators=200, max_depth=5)
    ↓
Evaluation: MAE, RMSE, R² (5-fold CV + test set)
    ↓
Error Analysis (top-15 worst predictions)

Unsupervised:
    Features → K-Means (K ∈ {3,4,5,6}) → silhouette → best K
    ↓
Cluster profiles (district, price, area, bedrooms)

Recommendation:
    Listings + User profile → Score (location + price + area) → Top-5
```

---

## Cài đặt

```bash
# Clone repo (hoặc vào thư mục dự án)
cd src/ChuoiKhoiUngDung

# Cài dependencies
python3 -m pip install -r requirements.txt

# Cài thêm để chạy notebook tự động (optional, nếu dùng run_all.sh)
python3 -m pip install nbformat nbclient ipykernel
```

### requirements.txt

```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
scikit-learn>=1.3.0
pytest>=7.4.0
jupyter>=1.0.0
```

---

## Chạy lại toàn bộ pipeline

### Cách 1 — Một lệnh duy nhất (khuyến nghị)

```bash
cd src/ChuoiKhoiUngDung
bash run_all.sh
```

Script này tự động:
1. Chạy 35 unit tests (`pytest tests/ -q`)
2. Chạy pipeline end-to-end (`python3 -m src.pipeline`)
3. Chạy cả 4 notebooks (lưu `*_executed.ipynb`)
4. Sinh toàn bộ output vào `reports/` + `data/processed/`

⏱️ Tổng thời gian: ~15–20 giây.

### Cách 2 — Chạy từng phần

**1. Chạy tests:**
```bash
python3 -m pytest tests/ -v
```

**2. Chạy pipeline end-to-end:**
```bash
python3 -m src.pipeline
```
Output:
- `data/processed/listings_clean.csv`
- `data/processed/listings_with_amenities.csv`
- `data/processed/listings_with_clusters.csv`
- `reports/metrics.json`
- `reports/sample_recommendations.csv`
- `data/logs/cleaning_log.csv` (mỗi lần chạy append thêm — backup nếu cần)

**3. Chạy notebooks (Jupyter UI):**
```bash
jupyter notebook notebooks/
# Mở lần lượt 01 → 02 → 03 → 04, nhấn "Run All Cells"
```

**4. Chạy notebooks (headless):**
```bash
python3 -c "
import nbformat
from nbclient import NotebookClient
for f in ['01_problem_and_data.ipynb','02_collection_and_cleaning.ipynb','03_eda.ipynb','04_machine_learning.ipynb']:
    print(f'--- {f} ---')
    nb = nbformat.read(f'notebooks/{f}', as_version=4)
    NotebookClient(nb, timeout=180, kernel_name='python3').execute()
    nbformat.write(nb, f'notebooks/{f.replace(\".ipynb\", \"_executed.ipynb\")}')
"
```

### Output files

| File | Mô tả |
|------|-------|
| `data/processed/listings_clean.csv` | Dữ liệu đã chuẩn hóa |
| `data/processed/listings_with_amenities.csv` | Merge tiện ích theo phường |
| `data/processed/listings_with_clusters.csv` | Có cluster_id |
| `reports/metrics.json` | MAE/RMSE/R² + silhouette scores |
| `reports/sample_recommendations.csv` | Top-5 cho 3 user profiles |
| `reports/figures/fig01–fig11.png` | 11 biểu đồ EDA + silhouette |
| `data/logs/cleaning_log.csv` | Nhật ký từng bước làm sạch |
| `data/logs/error_log.txt` | Lỗi phát hiện trong quá trình |

---

## Kết quả

### Data

| Chỉ tiêu | Giá trị |
|----------|---------|
| Tổng số tin | 3.000 |
| Thuộc tính | 13 (PropertyListing) |
| Quận/huyện | 24 quận TP.HCM |
| Phường/xã có amenities | 100 |
| Records sau outlier filter | ~2.950 |
| Coverage amenities | ~95% |

### Models (price_per_m2, VND, log-target)

| Model | Test MAE | Test RMSE | Test R² |
|-------|----------|-----------|---------|
| Baseline (Dummy mean) | 67.05M | 153.50M | -0.052 |
| Linear Regression | 49.93M | 126.53M | 0.285 |
| Random Forest | 43.66M | 117.11M | **0.388** |
| Gradient Boosting | 45.50M | 118.85M | 0.369 |

> **Best model:** Random Forest (R² = 0.388, RMSE ≈ 117 triệu VND/m²)

### Clustering (K-Means, auto-pick)

| K | Silhouette | Chọn? |
|---|------------|-------|
| 3 | **0.087** | ✅ (best) |
| 4 | 0.052 | — |
| 5 | 0.061 | — |
| 6 | 0.031 | — |

> **K=3** được chọn tự động. Các cluster đại diện 3 phân khúc giá/m² (thấp / trung cấp / cao cấp).

### Recommendation (top-5 cho 3 hồ sơ mẫu)

3 hồ sơ nhu cầu mẫu:
1. **Người mua đầu tư:** Quận vùng ven, giá thấp, diện tích lớn
2. **Gia đình trẻ:** Quận trung tâm, 3-4 phòng ngủ, tiện ích tốt
3. **Người mua cao cấp:** Quận 1/3/Bình Thạnh, diện tích lớn, hướng đẹp

Xem chi tiết trong `reports/sample_recommendations.csv`.

---

## Phân công

Đồ án đóng gói 1 thành viên. Chi tiết tại `reports/member_contributions.md`.

| Trục | Nhiệm vụ chính | Hoàn thành |
|------|----------------|------------|
| Data | Setup dự án + requirements + README | ✅ |
| Data | Tạo `neighborhood_amenities.csv` | ✅ |
| Data | Domain classes (`PropertyListing`, `Location`) | ✅ |
| Data | Cleaner: district + direction + outlier | ✅ |
| Data | `PropertyDataManager`: load + clean + merge + save | ✅ |
| Data | Feature pipeline (`ColumnTransformer`) | ✅ |
| Model | `PricePredictor`: Dummy + Linear + RF + GBR + CV | ✅ |
| Model | `KMeansSegmenter` + silhouette auto-pick K | ✅ |
| Model | `RecommendationEngine`: hybrid filter + scoring | ✅ |
| Model | Pipeline CLI end-to-end | ✅ |
| Cả hai | 4 notebooks + báo cáo + slide + dictionary + AI log | ✅ |

**Kiểm tra chéo:** 35 pytest tests (`pytest tests/ -v` → **35/35 PASS**).

**Trình bày:** Tối thiểu 7 phút × 1 người = 7 phút + Q&A.

---

## Giới hạn (A16)

1. **Dữ liệu tổng hợp** — không phải crawl web thật, chưa phản ánh biến động thị trường thực
2. **Features hạn chế** — thiếu text features (mô tả tin), ảnh, lịch sử giá
3. **R² thấp (0.39)** — giá BĐS phụ thuộc nhiều yếu tố không có trong data (vị trí chính xác, pháp lý, nội thất)
4. **Silhouette thấp (0.087)** — K-Means khó tách rõ phân khúc vì features hạn chế
5. **Recommendation đơn giản** — chỉ dùng rule-based scoring, chưa có collaborative filtering
6. **Thiếu temporal** — không xét biến động giá theo thời gian
7. **Không có text mining** — bỏ qua mô tả tin đăng (có thể chứa thông tin giá trị)

---

## AI Usage

Xem `reports/ai_usage_log.md` — ghi lại prompt, đầu ra AI, cách kiểm chứng và chỉnh sửa của dự án.