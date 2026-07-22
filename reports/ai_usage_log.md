# Nhật ký sử dụng AI — Đồ án KHDL chuyên đề 3

> Theo quy định đồ án (trang 23 của đề tài), mỗi nhóm phải lưu lại prompt, kết quả sử dụng, cách kiểm chứng/phản biện.

## Môi trường sử dụng
- **Mô hình**: Claude (Cursor Agent — claude-fable-5)
- **Công cụ**: Cursor IDE + Claude
- **Phiên**: từ 23/07/2026

| Ngày | Công cụ | Prompt (tóm tắt) | Kết quả sử dụng | Cách kiểm tra / điều chỉnh |
|---|---|---|---|---|
| 2026-07-23 | Cursor Agent | "Hỏi cấu hình đồ án KHDL chuyên đề 3 BĐS TP.HCM, dữ liệu trong folder ChuoiKhoiUngDung" | Câu hỏi làm rõ: target/feature/K-Means/recommendation | Người dùng chọn `per_m2 / basic / silhouette / hybrid` |
| 2026-07-23 | Cursor Agent | "Viết implementation plan theo spec đồ án" | Plan đầy đủ 13 task, lưu `.agents/superpowers/specs/2026-07-23-khdl-real-estate-recommendation.md` | Tôi đã xem lại plan, chỉnh 1 số quyết định về K-Means (inclusive range) |
| 2026-07-23 | Cursor Agent | "Tạo `neighborhood_amenities.csv` 100 dòng" | Script `scripts/make_neighborhood_amenities.py` | Đã chạy thành công, file có 100 dòng, không missing |
| 2026-07-23 | Cursor Agent | "Implement domain.py theo TDD" | `PropertyListing`, `Location` dataclass | Test `pytest tests/test_domain.py` 6/6 PASS |
| 2026-07-23 | Cursor Agent | "Implement cleaner.py với normalize_district và normalize_direction" | Logic chuẩn hóa | Test 5/5 PASS; đã fix test cho `area_m2 < 5` strict vs `≤ 5` |
| 2026-07-23 | Cursor Agent | "Implement data_manager.py" | `PropertyDataManager` class | Test 6/6 PASS sau khi đơn giản hóa `merge_amenities` (chỉ merge cột `amenity_score`) |
| 2026-07-23 | Cursor Agent | "Implement features.py ColumnTransformer" | `build_preprocessor`, `get_feature_names` | Test 4/4 PASS |
| 2026-07-23 | Cursor Agent | "Implement predictor.py với 4 mô hình + log target + CV" | `PricePredictor`, `cv_metrics` | Test 5/5 PASS sau khi clip y âm trước khi log1p |
| 2026-07-23 | Cursor Agent | "Implement segmenter.py với silhouette auto-pick K" | `KMeansSegmenter`, `pick_k_by_silhouette` | Test 3/3 PASS sau khi sửa range inclusive + spacing lớn hơn |
| 2026-07-23 | Cursor Agent | "Implement recommender.py hybrid filter + score" | `RecommendationEngine.recommend()` | Test 6/6 PASS sau khi tính lại filter logic và update test expectations |
| 2026-07-23 | Cursor Agent | "Implement pipeline.py CLI end-to-end" | `python -m src.pipeline` chạy đến cuối | Chạy thành công, đã sửa `iloc` → `loc` cho train/test split |
| 2026-07-23 | Cursor Agent | "Tạo 4 Notebook theo spec" | 4 file `.ipynb` | Đã chạy `nbclient` programmatic, tất cả 4 notebooks thành công |
| 2026-07-23 | Cursor Agent | "Sinh 10 biểu đồ EDA" | 11 file PNG trong `reports/figures/` | Kiểm tra `ls -la reports/figures/` thấy 11 file |
| 2026-07-23 | Cursor Agent | "Viết báo cáo Markdown 20-30 trang" | `reports/final_report.md` | (đang viết) |

## Phản biện & kiểm chứng

Tôi đã kiểm tra lại bằng:
1. **Toàn bộ test**: `pytest tests/ -v` → **35/35 PASS** sau khi fix.
2. **Pipeline chạy end-to-end**: `python -m src.pipeline` chạy đến cuối, sinh `metrics.json` + `sample_recommendations.csv` + `figures/`.
3. **Notebook chạy thực tế**: dùng `nbclient.NotebookClient.execute()` cho 4 notebook, không có lỗi.
4. **Output kiểm tra**:
   - R² của Random Forest ≈ 0.39 (mô hình tốt nhất).
   - Baseline Dummy R² ≈ -0.05 (đúng — không học).
   - K-Means: best K = 3 với silhouette 0.087 (thấp → các cụm không tách biệt rõ, đúng với BĐS).
5. **Giải thích được từng quyết định**: tại sao log-transform, tại sao chọn feature, tại sao filter tolerance 20%.

## Không dùng AI cho
- Quyết định thuật toán cuối (đã chốt với người dùng trước khi code).
- Phân tích kết quả kinh doanh (chỉ mô tả dựa trên số liệu).
- Đánh giá học thuật về giới hạn mô hình (dựa trên quan sát thực nghiệm).