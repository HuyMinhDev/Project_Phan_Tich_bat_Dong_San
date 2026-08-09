# Nhật ký sử dụng AI — Đồ án KHDL chuyên đề 3

> Theo quy định đồ án (trang 23 của đề tài), mỗi nhóm phải lưu lại prompt, kết quả sử dụng, cách kiểm chứng/phản biện.

## Môi trường sử dụng
- **Mô hình**: Cursor Agent (claude-fable-5)
- **Công cụ**: Cursor IDE + Claude
- **Phiên tổng**: 23/07/2026 → 08/08/2026

---

## Phiên 1 — 23/07/2026 (data nhà phố)

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
| 2026-07-23 | Cursor Agent | "Viết báo cáo Markdown 20-30 trang" | `reports/final_report.md` | Hoàn thành |

---

## Phiên 2 — 08/08/2026 (data căn hộ — phiên này)

| Ngày | Công cụ | Prompt (tóm tắt) | Kết quả sử dụng | Cách kiểm tra / điều chỉnh |
|---|---|---|---|---|
| 2026-08-08 | Cursor Agent | "Update project theo data mới `real_estate_with_price_per.xlsx` (căn hộ 6 quận, không phải nhà phố 24 quận cũ)" | Đề xuất 3 hướng: rewrite theo Chuyên đề 3 (căn hộ) / adapt code cũ / bỏ data cũ | Người dùng chọn (a) rewrite theo Chuyên đề 3 |
| 2026-08-08 | Cursor Agent | "Khám phá cấu trúc data xlsx mới" | Báo cáo: 1799 dòng × 32 cột, 6 quận, 1 loại hình, direction/furnishing/legal dạng mã số | Đã đối chiếu với schema cũ, xác định được cần thay đổi lớn |
| 2026-08-08 | Cursor Agent | "Update src/domain.py — đổi schema sang căn hộ" | `PropertyListing` 19 fields, bao gồm mã số (direction_code, balcony_code, furnishing_code, legal_code) | Test 9/9 PASS |
| 2026-08-08 | Cursor Agent | "Update src/cleaner.py — xử lý direction/furnishing/legal dạng code số" | `normalize_direction` (decode 1..8), `decode_furnishing` (1..4), `decode_legal` (1,2,4,5,6) | Test 9/9 PASS |
| 2026-08-08 | Cursor Agent | "Update src/data_manager.py + pipeline.py — thêm features mới" | Hỗ trợ đọc cả CSV và XLSX; NUMERIC_COLS có 9 cột (thêm direction_code, balcony_code, furnishing_code, legal_code, image_count, apartment_type) | Pipeline chạy OK |
| 2026-08-08 | Cursor Agent | "Update tests/ — 45 tests cho schema mới" | Sửa test_domain.py, test_cleaner.py, test_data_manager.py, test_features.py, test_recommender.py | 45/45 PASS |
| 2026-08-08 | Cursor Agent | "Update scripts/make_neighborhood_amenities.py cho xlsx" | Script đọc xlsx, tạo amenities mapping đúng 6 quận | Chạy sinh ra 89 dòng, 99% match rate |
| 2026-08-08 | Cursor Agent | "Update 4 notebooks cho schema căn hộ" | 4 file `.ipynb` mới với features mới | Chạy qua nbclient, 4/4 OK |
| 2026-08-08 | Cursor Agent | "Update README + reports với data mới" | README.md, final_report.md, data_dictionary.md, slide_outline.md, member_contributions.md | Đã cập nhật |

## Phản biện & kiểm chứng

Tôi đã kiểm tra lại bằng:
1. **Toàn bộ test**: `pytest tests/ -v` → **45/45 PASS** (sau khi fix 3 lỗi test ban đầu liên quan encoding và test count).
2. **Pipeline chạy end-to-end**: `python3 -m src.pipeline` chạy đến cuối, sinh `metrics.json` + `sample_recommendations.csv` + 12 figures.
3. **Notebook chạy thực tế**: dùng `nbclient.NotebookClient.execute()` cho 4 notebook, không có lỗi.
4. **Output kiểm tra**:
   - R² của Random Forest ≈ 0.169 (mô hình tốt nhất trên test).
   - Baseline Dummy R² ≈ -0.041 (đúng — không học).
   - K-Means: best K = 4 với silhouette 0.083 (thấp → các cụm không tách biệt rõ, đúng với BĐS).
   - Coverage amenities: 1763/1779 = 99% (tốt hơn nhiều so với data cũ 67%).
5. **Giải thích được từng quyết định**: tại sao log-transform, tại sao chọn feature, tại sao filter tolerance 20%, tại sao schema mới cần thêm mã số.

## Không dùng AI cho

- Quyết định thuật toán cuối (đã chốt với người dùng trước khi code).
- Phân tích kết quả kinh doanh (chỉ mô tả dựa trên số liệu).
- Đánh giá học thuật về giới hạn mô hình (dựa trên quan sát thực nghiệm).
