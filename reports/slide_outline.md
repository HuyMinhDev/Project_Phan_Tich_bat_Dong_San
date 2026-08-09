# Slide outline — Báo cáo đồ án KHDL cuối kỳ
**Chuyên đề 3: Phân tích và gợi ý bất động sản Căn hộ/Chung cư TP.HCM**

> Mỗi slide = tiêu đề + 5-7 dòng nội dung + 1 hình minh họa. Slide 1-2 giới thiệu, 3-6 phương pháp, 7-9 kết quả, 10-11 kết luận + hướng phát triển.

---

## Slide 1: Trang bìa
- **Đồ án KHDL cuối kỳ — Chuyên đề 3**
- Phân tích và gợi ý bất động sản Căn hộ/Chung cư TP.HCM
- Học viên: [Điền tên]
- Giảng viên: [Điền tên]
- Ngày: 08/08/2026
- *Hình: logo trường / BĐS TP.HCM*

---

## Slide 2: Bối cảnh & mục tiêu
- Căn hộ TP.HCM có giá không đồng nhất, hướng/nội thất/pháp lý dạng mã số, nhiều outlier
- Mục tiêu: (1) chuẩn hóa + decode mã; (2) dự đoán `price_per_m2`; (3) phân khúc K-Means; (4) gợi ý top 5 theo nhu cầu
- Ứng dụng: hỗ trợ người mua/nhà đầu tư tìm căn hộ phù hợp
- *Hình: ví dụ tin thô vs tin sạch*

---

## Slide 3: Dữ liệu
- **Nguồn 1**: 1799 tin căn hộ TP.HCM, 32 cột (`real_estate_apartment.xlsx`)
- **Nguồn 2**: 89 dòng thông tin tiện ích theo (quận, phường) — tự tạo deterministic
- 6 quận (Thủ Đức, Bình Thạnh, Quận 7, Gò Vấp, Quận 12, Bình Tân), 83 phường
- Missing nhiều ở `direction` (79%), `balcony_direction` (73%), `furnishing_status` (34%)
- *Hình: bảng 5 dòng đầu của dataset*

---

## Slide 4: Pipeline làm sạch
- Bước 1: chuẩn hóa `district` (pass-through), `direction` (1..8 → 8 hướng chính)
- Bước 2: decode mã `furnishing_status` (1..4) và `legal_status` (1,2,4,5,6) → nhãn tiếng Việt
- Bước 3: lọc outlier (area < 10 hoặc > 500, price < 100tr, bedrooms > 10)
- Bước 4: tính lại `price_per_m2 = total_price / area_m2`
- Bước 5: merge `amenity_score` (left-join) — match **1763/1779 ≈ 99%**
- Kết quả: **1779 dòng sạch** từ 1799 (~20 dòng loại)
- *Hình: sơ đồ pipeline*

---

## Slide 5: Phương pháp ML
- **Target**: `log1p(price_per_m2)` (giảm skewness)
- **Features**: 9 numeric + 3 categorical (OHE với `min_frequency=10`)
- **Pipeline sklearn**: `ColumnTransformer` (impute + scale + OHE)
- **4 mô hình so sánh**: Dummy (baseline median), Linear, Random Forest, Gradient Boosting
- **Đánh giá**: 5-fold CV trên train + 1 lần trên test
- *Hình: bảng so sánh MAE/RMSE/R²*

---

## Slide 6: Kết quả mô hình
| Model | CV MAE | Test MAE | Test RMSE | Test R² |
|---|---|---|---|---|
| Dummy (baseline) | 18.5M | 18.5M | 37.1M | **-0.041** |
| Linear | 14.1M | 14.9M | 33.7M | 0.143 |
| **Random Forest** | **13.0M** | **13.9M** | **33.2M** | **0.169** |
| Gradient Boosting | 13.4M | 14.4M | 33.7M | 0.162 |

- Random Forest tốt nhất (R²=0.169) — phù hợp với dữ liệu căn hộ thực tế
- Baseline Dummy R² âm → đúng (không học)
- *Hình: bảng kết quả + scatter predicted vs actual*

---

## Slide 7: Phân tích 10 trường hợp sai lớn nhất
- Phần lớn sai ở căn giá cực cao (> 150tr/m²) — mô hình dự đoán thấp hơn 30-60%
- Căn diện tích nhỏ (~50m²) ở vị trí đắt đỏ (Thủ Đức, Bình Thạnh) — mô hình dựa vào "diện tích" làm feature trung bình
- Tin thiếu nhiều thông tin → impute median gây sai lệch
- *Hình: bảng 10 dòng có %error cao nhất*

---

## Slide 8: Phân cụm K-Means
- Best K = **4** (silhouette = 0.083)
- Cluster 0: 165 tin (căn nhỏ, giá trung bình)
- Cluster 1: 1396 tin (đa số — căn 2PN trung cấp)
- Cluster 2: 47 tin (căn cao cấp, penthouse)
- Cluster 3: 165 tin (căn lớn, diện tích > 80m²)
- Silhouette thấp → các cụm không tách biệt rõ (đúng với BĐS liên tục)
- *Hình: line chart silhouette + bar cluster counts*

---

## Slide 9: Hệ gợi ý top 5 — 3 hồ sơ demo
- Profile 1: Gia đình trẻ, 3 tỷ, Thủ Đức / Bình Thạnh → top 5 trong quận + cụm 0
- Profile 2: Nhà đầu tư, 5 tỷ, Quận 7 / Bình Tân → top 5 trong cụm 1
- Profile 3: Người mua cao cấp, 7 tỷ, Thủ Đức / Quận 7 → top 5 trong cụm 2
- Cả 3 profile đều có kết quả — phù hợp với phạm vi 6 quận căn hộ
- Score: 4 thành phần (giá, diện tích, cụm, tiện ích)
- *Hình: bảng top 5 cho 2 profile đầu*

---

## Slide 10: Giới hạn & rủi ro
- **Dữ liệu**: 1799 dòng, 1 nguồn (chotot) → mô hình yếu với giá cực trị
- **Phạm vi 6 quận**: thiếu các quận trung tâm (1, 3, 4, 5) → bias tier giá
- **Snapshot T7-T8/2026**: không phân tích xu hướng theo thời gian
- **Missing cao**: direction 79% → impute median có thể bias
- **Rủi ro thiên lệch**: cluster 1 chiếm 78% → K-Means không tách rõ phân khúc
- **Không triển khai thực tế**: chỉ dùng để minh họa pipeline KHDL

---

## Slide 11: Kết luận & hướng phát triển
- ✅ Pipeline chuẩn hóa hoàn chỉnh cho căn hộ (decode mã số + outlier), OOP, có test (45/45)
- ✅ Mô hình dự đoán hoạt động (R²=0.169 — phù hợp với dữ liệu căn hộ)
- ✅ Hệ gợi ý hybrid có bonus cụm + tiện ích (3/3 profile match)
- Hướng phát triển:
  - Thu thập ≥10.000 tin, mở rộng 24 quận TP.HCM
  - Thêm feature khoảng cách đến trung tâm (từ lat/lon)
  - Thêm tầng, view, tiến độ dự án
  - Thử XGBoost / LightGBM
  - Trích đặc trưng từ `description` (NLP)
- *Hình: kiến trúc hệ thống mở rộng*

---

## Slide 12: Q&A
- Cảm ơn đã lắng nghe!
- Liên hệ: [Điền email]
- Tài liệu tham khảo:
  - Scikit-learn documentation (ColumnTransformer, Pipeline)
  - `real_estate_apartment.xlsx` (snapshot T7-T8/2026 từ chotot)
  - `reports/final_report.md` (báo cáo đầy đủ)
