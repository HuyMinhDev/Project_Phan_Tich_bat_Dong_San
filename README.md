"""Đồ án KHDL cuối kỳ — Chuyên đề 3: Phân tích và gợi ý bất động sản TP.HCM.

## Mục tiêu
Xây dựng hệ thống phân tích và gợi ý tin đăng bất động sản nhà phố tại TP.HCM,
gồm các bước: chuẩn hóa dữ liệu, EDA, mô hình dự đoán giá/m², phân cụm phân khúc,
hệ gợi ý top 5 theo hồ sơ nhu cầu — kèm 4 Notebook, báo cáo Markdown, slide outline.

## Dữ liệu
- `data/raw/real_estate_with_price_per_m2.csv` — 3000 tin BĐS nhà phố TP.HCM (nguồn chính).
- `data/raw/neighborhood_amenities.csv` — thông tin tiện ích theo phường/xã (nguồn phụ, tự tạo).

## Cấu trúc thư mục
```
ChuoiKhoiUngDung/
├── data/
│   ├── raw/                          # dữ liệu thô
│   ├── processed/                    # dữ liệu sạch
│   └── logs/                         # cleaning_log.csv, error_log.txt
├── src/
│   ├── domain.py                     # PropertyListing, Location
│   ├── cleaner.py                    # quy tắc chuẩn hóa
│   ├── data_manager.py               # PropertyDataManager
│   ├── features.py                   # ColumnTransformer pipeline
│   ├── predictor.py                  # PricePredictor (Dummy + Lin + RF + GBR)
│   ├── segmenter.py                  # KMeansSegmenter
│   ├── recommender.py                # RecommendationEngine
│   └── pipeline.py                   # CLI end-to-end
├── notebooks/
│   ├── 01_problem_and_data.ipynb
│   ├── 02_collection_and_cleaning.ipynb
│   ├── 03_eda.ipynb
│   └── 04_machine_learning.ipynb
├── tests/                            # pytest
├── reports/
│   ├── figures/                      # PNG biểu đồ
│   ├── final_report.md
│   ├── slide_outline.md
│   ├── metrics.json
│   ├── data_dictionary.md
│   ├── ai_usage_log.md
│   └── member_contributions.md
├── requirements.txt
└── README.md
```

## Cài đặt
```bash
cd ChuoiKhoiUngDung
python3 -m pip install -r requirements.txt
```

## Chạy pipeline end-to-end
```bash
python -m src.pipeline \
  --data-path data/raw/real_estate_with_price_per_m2.csv \
  --amenities-path data/raw/neighborhood_amenities.csv \
  --output-dir data/processed \
  --reports-dir reports
```

Sau khi chạy xong, các file sinh ra:
- `data/processed/listings_with_amenities.csv` — dữ liệu sạch có merge tiện ích
- `data/logs/cleaning_log.csv` — nhật ký từng bước làm sạch
- `data/logs/error_log.txt` — lỗi phát hiện trong quá trình
- `reports/metrics.json` — MAE/RMSE/R² cho 4 model + K-Means silhouette
- `reports/sample_recommendations.csv` — top 5 cho 3 hồ sơ nhu cầu mẫu
- `reports/figures/*.png` — 8+ biểu đồ EDA

## Chạy test
```bash
pytest tests/ -v
```

## Chạy Notebook
Mở từng file trong `notebooks/` theo thứ tự 01 → 04, chạy `Run All Cells`.
"""