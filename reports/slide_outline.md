# Slide outline — Báo cáo đồ án KHDL cuối kỳ
**Chuyên đề 3: Phân tích và gợi ý bất động sản TP.HCM**

> Mỗi slide = tiêu đề + 5-7 dòng nội dung + 1 hình minh họa. Slide 1-2 giới thiệu, 3-6 phương pháp, 7-9 kết quả, 10-11 kết luận + hướng phát triển.

---

## Slide 1: Trang bìa
- **Đồ án KHDL cuối kỳ — Chuyên đề 3**
- Phân tích và gợi ý bất động sản TP.HCM
- Học viên: [Điền tên]
- Giảng viên: [Điền tên]
- Ngày: 23/07/2026
- *Hình: logo trường / BĐS TP.HCM*

---

## Slide 2: Bối cảnh & mục tiêu
- Tin BĐS có giá không đồng nhất, địa danh viết tắt, nhiều tin trùng, outlier rõ
- Mục tiêu: (1) chuẩn hóa; (2) dự đoán `price_per_m2`; (3) phân khúc K-Means; (4) gợi ý top 5 theo nhu cầu
- Ứng dụng: hỗ trợ người mua/nhà đầu tư tìm BĐS phù hợp
- *Hình: ví dụ tin thô vs tin sạch*

---

## Slide 3: Dữ liệu
- **Nguồn 1**: 3000 tin nhà phố TP.HCM, 20 cột (`real_estate_with_price_per_m2.csv`)
- **Nguồn 2**: 100 dòng thông tin tiện ích theo (quận, phường) — tự tạo deterministic
- 22 quận/huyện, 144 phường/xã
- Missing nhiều ở `house_depth` (99.6%), `project_name` (98.6%)
- *Hình: bảng 5 dòng đầu của dataset*

---

## Slide 4: Pipeline làm sạch
- Bước 1: chuẩn hóa `district` (số → "Quận X"), `house_direction` (8 hướng)
- Bước 2: lọc outlier (area < 5 hoặc > 1000, price < 100tr, bedrooms > 15)
- Bước 3: tính lại `price_per_m2 = total_price / area_m2`
- Bước 4: merge `amenity_score` (left-join) — match 1987/2968 ≈ 67%
- Kết quả: **2968 dòng sạch** từ 3000 (~32 dòng loại)
- *Hình: sơ đồ pipeline*

---

## Slide 5: Phương pháp ML
- **Target**: `log1p(price_per_m2)` (giảm skewness)
- **Features**: 5 numeric + 2 categorical (OHE với `min_frequency=10`)
- **Pipeline sklearn**: `ColumnTransformer` (impute + scale + OHE)
- **4 mô hình so sánh**: Dummy (baseline median), Linear, Random Forest, Gradient Boosting
- **Đánh giá**: 5-fold CV trên train + 1 lần trên test
- *Hình: bảng so sánh MAE/RMSE/R²*

---

## Slide 6: Kết quả mô hình
| Model | CV MAE | Test MAE | Test RMSE | Test R² |
|---|---|---|---|---|
| Dummy (baseline) | 63M | 67M | — | **-0.05** |
| Linear | 48M | 50M | — | 0.29 |
| **Random Forest** | **43M** | **44M** | — | **0.39** |
| Gradient Boosting | 44M | 46M | — | 0.37 |

- Random Forest tốt nhất (R²=0.39)
- Baseline Dummy R² âm → đúng (không học)
- *Hình: bảng kết quả + scatter predicted vs actual*

---

## Slide 7: Phân tích 10 trường hợp sai lớn nhất
- Phần lớn sai ở căn giá cực cao (> 300tr/m²) — mô hình dự đoán thấp hơn nhiều
- Căn diện tích lớn ở vùng ven cũng sai (mô hình đánh giá quá cao)
- Tin thiếu thông tin → impute median gây sai lệch
- *Hình: bảng 10 dòng có %error cao nhất*

---

## Slide 8: Phân cụm K-Means
- Best K = **3** (silhouette = 0.087)
- Cluster 0: 50 tin (rất nhỏ — outlier khu trung tâm)
- Cluster 1: 1100 tin (trung cấp)
- Cluster 2: 1792 tin (phổ thông)
- Silhouette thấp → các cụm không tách biệt rõ (đúng với BĐS liên tục)
- *Hình: line chart silhouette + bar cluster counts*

---

## Slide 9: Hệ gợi ý top 5 — 3 hồ sơ demo
- Profile 1: Gia đình trẻ, 5 tỷ, Quận 7 / Bình Thạnh → top 5 trong quận + cụm 1
- Profile 2: Nhà đầu tư, 8 tỷ, Quận 2 / 9 → top 5 trong cụm 0
- Profile 3: Người mua đầu tiên, 3 tỷ, ngoại thành → không match (giá quá thấp → hạn chế)
- Score: 4 thành phần (giá, diện tích, cụm, tiện ích)
- *Hình: bảng top 5 cho 2 profile đầu*

---

## Slide 10: Giới hạn & rủi ro
- **Dữ liệu**: 3000 dòng, 1 nguồn → mô hình yếu với giá cực trị
- **Snapshot T6/2025**: không phân tích xu hướng theo thời gian
- **Pháp lý / nội thất**: thiếu trong dataset — không dùng làm feature
- **Tọa độ**: không có → không vẽ bản đồ choropleth
- **Rủi ro thiên lệch**: cluster 0 quá nhỏ (50 tin) → bonus có thể không công bằng
- **Không triển khai thực tế**: chỉ dùng để minh họa pipeline KHDL

---

## Slide 11: Kết luận & hướng phát triển
- ✅ Pipeline chuẩn hóa hoàn chỉnh, OOP, có test (35/35)
- ✅ Mô hình dự đoán hoạt động (R²=0.39)
- ✅ Hệ gợi ý hybrid có bonus cụm + tiện ích
- Hướng phát triển:
  - Thu thập ≥10.000 tin (nhiều nguồn)
  - Thêm feature khoảng cách đến trung tâm (lat/lon)
  - Thử XGBoost / LightGBM
  - Thêm trích xuất đặc trưng từ `description` (NLP)
  - Phân tích pháp lý / nội thất qua regex từ mô tả
- *Hình: kiến trúc hệ thống mở rộng*

---

## Slide 12: Q&A
- Cảm ơn đã lắng nghe!
- Liên hệ: [Điền email]
- Tài liệu tham khảo:
  - Scikit-learn documentation (ColumnTransformer, Pipeline)
  - `real_estate_with_price_per_m2.csv` (snapshot T6/2025)
  - `reports/final_report.md` (báo cáo đầy đủ 20-30 trang)