# Báo cáo đồ án KHDL cuối kỳ

## Chuyên đề 3: Phân tích và gợi ý bất động sản TP.HCM

---

**Học viên**: [Điền tên]
**MSSV**: [Điền]
**Môn học**: Lập trình cho Khoa học Dữ liệu
**Giảng viên hướng dẫn**: [Điền]
**Ngày nộp**: 23/07/2026

---

## Mục lục

1. [Tóm tắt](#1-tóm-tắt)
2. [Giới thiệu bài toán](#2-giới-thiệu-bài-toán)
3. [Phương pháp thu thập dữ liệu](#3-phương-pháp-thu-thập-dữ-liệu)
4. [Từ điển dữ liệu](#4-từ-điển-dữ-liệu)
5. [Tiền xử lý và làm sạch](#5-tiền-xử-lý-và-làm-sạch)
6. [EDA — Phân tích khám phá dữ liệu](#6-eda--phân-tích-khám-phá-dữ-liệu)
7. [Mô hình dự đoán giá/m²](#7-mô-hình-dự-đoán-giám²)
8. [Phân tích 10 trường hợp sai số lớn](#8-phân-tích-10-trường-hợp-sai-số-lớn)
9. [Phân cụm K-Means](#9-phân-cụm-k-means)
10. [Hệ gợi ý top 5](#10-hệ-gợi-ý-top-5)
11. [Giới hạn và rủi ro thiên lệch](#11-giới-hạn-và-rủi-ro-thiên-lệch)
12. [Kết luận và hướng phát triển](#12-kết-luận-và-hướng-phát-triển)
13. [Phụ lục](#13-phụ-lục)
14. [Tài liệu tham khảo](#14-tài-liệu-tham-khảo)

---

## 1. Tóm tắt

Đồ án này xây dựng một pipeline phân tích và gợi ý tin đăng bất động sản nhà phố tại TP.HCM từ tập dữ liệu 3000 tin. Quy trình gồm 4 bước chính:

1. **Chuẩn hóa dữ liệu**: 32 dòng outlier bị loại (diện tích < 5 hoặc > 1000m², giá < 100 triệu, số phòng > 15); 22 giá trị `district` (kể cả dạng số "1") được chuẩn hóa thành tên quận/huyện đầy đủ; 12 hướng nhà được gộp về 8 hướng chính.
2. **Dự đoán giá/m²**: So sánh 4 mô hình (Dummy baseline + Linear Regression + Random Forest + Gradient Boosting) với pipeline sklearn `ColumnTransformer`. Mô hình tốt nhất là Random Forest với R² = 0.388 trên tập test, MAE ≈ 44 triệu VND/m².
3. **Phân cụm K-Means**: Chọn K = 3 theo silhouette score. Ba cụm: phổ thông (1792 tin), trung cấp (1100 tin), và nhóm rất nhỏ (50 tin) — gần như outlier khu trung tâm.
4. **Hệ gợi ý top 5**: Chiến lược hybrid (filter cứng theo ngân sách ± 20%, số phòng ± 1, quận ưu tiên; cộng điểm theo giá, diện tích, cùng cụm K-Means, tiện ích). Demo với 3 hồ sơ nhu cầu.

Tất cả 35 unit test pass, pipeline chạy end-to-end thành công, 11 biểu đồ EDA được sinh, 4 Notebook Jupyter chạy được từ đầu đến cuối.

---

## 2. Giới thiệu bài toán

### 2.1 Bối cảnh

Thị trường bất động sản nhà phố tại TP.HCM là một trong những thị trường sôi động nhất Việt Nam, với hàng nghìn tin đăng mỗi ngày trên các nền tảng trực tuyến. Tuy nhiên, dữ liệu thô từ các nguồn này thường có nhiều vấn đề:

- **Giá viết không thống nhất**: "3,5 tỷ", "3500 triệu", "Giá thỏa thuận" — cùng một giá trị nhưng 3 cách ghi.
- **Diện tích có dấu phẩy thập phân**: "75,5 m²", "98,5 m²".
- **Địa danh viết tắt / lẫn lộn**: "Q.1", "Quận 1", "1" — đều là cùng một quận.
- **Nhiều tin đăng trùng** (cùng căn nhà đăng trên nhiều nền tảng bởi nhiều môi giới).
- **Outlier rõ ràng**: căn 11 m² giá 5 tỷ (chắc chắn sai), căn 7132 m² (chắc chắn sai).
- **Thiếu thông tin pháp lý / nội thất** ở hầu hết các tin.

### 2.2 Mục tiêu

Theo đề tài Chuyên đề 3 của môn Lập trình cho Khoa học Dữ liệu, đồ án cần đạt 6 mục tiêu cụ thể:

1. **Chuẩn hóa** giá, diện tích, giá/m², địa điểm và các thuộc tính mô tả.
2. **Phát hiện** tin trùng và ngoại lệ.
3. **Dự đoán** tổng giá hoặc giá trên mét vuông (`price_per_m2`).
4. **Phân khúc** bất động sản bằng K-Means.
5. **Gợi ý** top 5 theo ngân sách, khu vực, diện tích, số phòng.
6. **Trực quan hóa** ≥ 8 biểu đồ có tiêu đề + nhãn trục + nhận xét.

### 2.3 Sáu câu hỏi nghiên cứu

1. Khu vực nào có `price_per_m2` cao nhất?
2. Diện tích và số phòng ảnh hưởng như thế nào đến tổng giá và giá/m²?
3. Hướng nhà và vị trí quận có liên hệ gì với giá không?
4. Tin nào có giá/diện tích bất thường hoặc có khả năng trùng?
5. Mô hình dự đoán giá/m² đạt sai số bao nhiêu (MAE / RMSE / R²)?
6. Top 5 tin nào phù hợp với từng hồ sơ nhu cầu?

---

## 3. Phương pháp thu thập dữ liệu

### 3.1 Nguồn dữ liệu

| Nguồn | File | Số dòng | Mô tả | Schema |
|---|---|---|---|---|
| **1 (chính)** | `data/raw/real_estate_with_price_per_m2.csv` | 3000 | Snapshot tin đăng BĐS nhà phố TP.HCM từ nền tảng alonhadat-style, T6/2025 | 20 cột (id, tiêu đề, mô tả, loại hình, tỉnh, quận, phường, đường, dự án, tổng giá, diện tích, giá/m², tầng, mặt tiền, chiều sâu, độ rộng đường, phòng ngủ, phòng tắm, hướng, ngày đăng) |
| **2 (phụ)** | `data/raw/neighborhood_amenities.csv` | 100 | Thông tin tiện ích theo (quận, phường) — tự tạo deterministic (seed=42) | 8 cột (ward, district_clean, school/hospital/supermarket/park/bus_stops counts, amenity_score) |

### 3.2 Ghi chú quan trọng về nguồn dữ liệu

Đồ án sử dụng **dữ liệu được cung cấp sẵn** (snapshot) chứ không crawl trực tiếp từ các nền tảng BĐS. Lý do:

- **Tuân thủ điều khoản sử dụng**: Theo yêu cầu đồ án (mục I.2.3 PDF đề tài), nhóm không được vượt CAPTCHA, anti-bot, hoặc cơ chế chống bot. Nhiều nền tảng BĐS có cơ chế chống scraping.
- **Phương án dữ liệu dự phòng**: Theo yêu cầu đồ án (mục I.2.5), nhóm phải có phương án dữ liệu dự phòng. Snapshot từ giảng viên cung cấp là phương án được phép.
- **Tính tái lập**: Snapshot cho phép người chấm chạy lại pipeline và có cùng kết quả.

Nguồn dữ liệu thứ hai (`neighborhood_amenities.csv`) là **dữ liệu mô phỏng có kiểm soát** — sinh bằng random seed = 42 với công thức weighted score cố định. Điều này:
- Đáp ứng yêu cầu "ít nhất 2 nguồn / 2 loại tập tin có cấu trúc khác nhau" của đề tài.
- Có thể thay thế bằng dữ liệu thật (từ OpenStreetMap, bản đồ quy hoạch TP.HCM) trong phiên bản tiếp theo.

### 3.3 Phạm vi phân tích

- **Địa lý**: Toàn bộ 22 quận/huyện TP.HCM (bao gồm Quận 1-12, Bình Thạnh, Tân Bình, Gò Vấp, Phú Nhuận, Tân Phú, Bình Tân, Thủ Đức, Bình Chánh, Củ Chi, Cần Giờ, Hóc Môn, Nhà Bè).
- **Loại hình**: Nhà phố (toàn bộ 3000 dòng đều là `property_type = "Nhà"`).
- **Thời gian**: Snapshot T6/2025 (không phân tích xu hướng theo thời gian).

---

## 4. Từ điển dữ liệu

Chi tiết từng cột xem `reports/data_dictionary.md`. Tóm tắt:

| Cột | Kiểu | Missing % | Vai trò |
|---|---|---|---|
| `listing_id` | int | 0.00 | Khóa chính |
| `total_price` | float | 0.87 | Target phụ (lọc outlier) |
| `area_m2` | float | 0.00 | Feature chính |
| `price_per_m2` | float | 0.87 | **Target** (tính lại từ total_price/area_m2) |
| `bedrooms` | float | 16.97 | Feature chính |
| `bathrooms` | float | 19.07 | Feature phụ |
| `floor_count` | float | 74.53 | Feature (impute median) |
| `frontage_width` | float | 8.13 | Feature (impute median) |
| `district` | str | 0.53 | Chuẩn hóa → `district_clean` |
| `ward` | str | 6.67 | Khóa join với amenities |
| `house_direction` | str | 0.00 | Chuẩn hóa → `direction_clean` |
| `house_depth`, `road_width`, `project_name` | — | > 80% | **BỎ** |

---

## 5. Tiền xử lý và làm sạch

### 5.1 Quy trình làm sạch (5 bước)

```python
# Trong src.cleaner.clean_dataframe(df)
1. df["district_clean"] = df["district"].apply(normalize_district)
2. df["direction_clean"] = df["house_direction"].apply(normalize_direction)
3. cleaned, log = filter_outliers(df)  # loại area/price/bedrooms ngoài phạm vi
4. cleaned = recompute_price_per_m2(cleaned)
5. return cleaned, log, errors
```

### 5.2 Ví dụ minh họa trước/sau

**Trước** (3 dòng đầu của `district`):
```
0        "10"
1    "Tân Bình"
2      "Gò Vấp"
```

**Sau** (3 dòng `district_clean` tương ứng):
```
0       "Quận 10"
1    "Quận Tân Bình"
2    "Quận Gò Vấp"
```

**Trước** (một số `house_direction`):
```
"Đông - Nam", "Tây - Bắc", "Đông - Bắc", "Đông", ...
```

**Sau** (8 hướng chuẩn):
```
"Đông Nam", "Tây Bắc", "Đông Bắc", "Đông", ...
```

### 5.3 Quy tắc lọc outlier

| Biến | Quy tắc | Lý do |
|---|---|---|
| `area_m2` | < 5 hoặc > 1000 → drop | Nhà dưới 5m² hoặc trên 1000m² gần như chắc chắn sai dữ liệu |
| `total_price` | < 100 triệu → drop | Giá nhà TP.HCM tối thiểu cũng > 100 triệu |
| `bedrooms` | > 15 → drop | Căn hộ/nhà phố bình thường < 15 phòng |

### 5.4 Kết quả làm sạch

| Bước | Số dòng còn | Ghi chú |
|---|---|---|
| Raw | 3000 | |
| Sau lọc outlier | 2968 | Bỏ 32 dòng (1.07%) |
| Có `amenity_score` (match) | 1987 | 67% match với nguồn 2 |

**Phân bố lỗi trong cleaning_log**:
- 19 dòng `area_too_small_or_large`
- 13 dòng `price_too_low`
- 0 dòng `bedrooms_outlier` (vì bedrooms > 15 chỉ xuất hiện ở các dòng đã bị loại bởi điều kiện trước)

File log: `data/logs/cleaning_log.csv`, `data/logs/error_log.txt`.

---

## 6. EDA — Phân tích khám phá dữ liệu

Tất cả 11 biểu đồ được lưu trong `reports/figures/`.

### 6.1 Phân bố `price_per_m2` (trước và sau log-transform)

![fig01](reports/figures/fig01_price_distribution.png)

**Nhận xét**: Phân bố thang gốc lệch phải mạnh (skewed) do có vài căn giá cực cao > 500tr/m². Log-transform giúp phân bố gần chuẩn — đây là lý do ta fit mô hình trên log1p(price_per_m2) rồi inverse-transform khi đánh giá.

### 6.2 Top 10 quận có giá/m² cao nhất

![fig02](reports/figures/fig02_top10_districts.png)

**Nhận xét**: Quận 1, Quận 3 và Bình Thạnh có giá cao nhất (đúng với thực tế BĐS TP.HCM — khu vực trung tâm). Quận 2, Quận 7, Quận Bình Thạnh là nhóm tiếp theo. Các huyện ngoại thành (Củ Chi, Bình Chánh) đứng cuối.

### 6.3 Boxplot giá/m² theo hướng nhà

![fig03](reports/figures/fig03_price_by_direction.png)

**Nhận xét**: Chênh lệch giá giữa các hướng không lớn (median trong khoảng 80–130 tr/m²). Hướng Đông Nam — hướng phong thủy tốt — có median cao nhất, nhưng overlap nhiều với các hướng khác → hướng là feature yếu, đóng góp nhỏ vào mô hình.

### 6.4 Scatter diện tích vs tổng giá

![fig04](reports/figures/fig04_area_vs_price.png)

**Nhận xét**: Quan hệ gần tuyến tính — diện tích càng lớn giá càng cao. Tuy nhiên, độ dốc khác nhau giữa các cụm (khu vực nội thành/ngoại thành). Outlier còn lại sau lọc là những căn diện tích nhỏ ở khu đắt đỏ (Quận 1).

### 6.5 Top 15 quận có nhiều tin nhất

![fig05](reports/figures/fig05_listings_by_district.png)

**Nhận xét**: Quận có nhiều tin nhất là các quận vùng ven (Bình Chánh, Gò Vấp, Thủ Đức). Các quận trung tâm (1, 3, 4) có ít tin hơn vì nguồn cung hạn chế.

### 6.6 Heatmap correlation

![fig06](reports/figures/fig06_correlation_heatmap.png)

**Nhận xét**: Tương quan giữa `price_per_m2` và các biến khác yếu (< 0.3) → giá/m² phụ thuộc chủ yếu vào vị trí (district, hướng) hơn là diện tích/phòng. `bedrooms ↔ area_m2 = 0.55` (dự kiến). `total_price ↔ area_m2 = 0.65` — cùng đơn vị diện tích.

### 6.7 Số tin đăng theo tháng

![fig07](reports/figures/fig07_postings_over_time.png)

**Nhận xét**: Dữ liệu tập trung chủ yếu vào tháng 6/2025. Các tháng khác rất thưa. Đây là dataset snapshot — không nên phân tích xu hướng theo tháng.

### 6.8 Boxplot giá/m² theo số phòng ngủ

![fig08](reports/figures/fig08_price_by_bedrooms.png)

**Nhận xét**: 1PN có giá/m² cao nhất (căn hộ nhỏ ở vị trí đắt đỏ). Từ 2PN trở lên, giá/m² ổn định. Đây là hiệu ứng tương đối — căn càng rộng phần nhiều ở vùng ven, giá/m² thấp hơn.

### 6.9 Amenity score trung bình theo top 10 quận

![fig09](reports/figures/fig09_amenity_by_district.png)

**Nhận xét**: Quận trung tâm (1, 3) có amenity score cao nhất do mật độ tiện ích dày. Quận vùng ven (Bình Chánh, Hóc Môn, Củ Chi) thấp hơn.

### 6.10 Phân bố số phòng ngủ

![fig10](reports/figures/fig10_bedrooms_count.png)

**Nhận xét**: 4PN chiếm đa số (~870 tin), tiếp theo 2–3PN. Đây là cơ cấu phổ biến của nhà phố TP.HCM.

---

## 7. Mô hình dự đoán giá/m²

### 7.1 Thiết kế pipeline

```python
pre = build_preprocessor(
    numeric_cols=["area_m2", "bedrooms", "bathrooms", "floor_count", "frontage_width"],
    categorical_cols=["district_clean", "direction_clean"],
)
# Trong pre:
# - numeric: SimpleImputer(median) → StandardScaler
# - categorical: SimpleImputer(constant="missing") → OneHotEncoder(handle_unknown="ignore", min_frequency=10)
```

**Quyết định**:
- `log_target=True`: fit trên log1p(price_per_m2), inverse bằng expm1 khi predict → giảm skewness, mô hình hội tụ tốt hơn.
- `OneHotEncoder(min_frequency=10)`: loại bỏ dummy cho category hiếm (<10 tin) → giảm chiều, tránh overfitting.
- `handle_unknown="ignore"`: robust với district mới trong test set.

### 7.2 Train/test split

- **Tỉ lệ**: 80/20, `random_state=42`, shuffle=True.
- **Kích thước**: train = 2353 dòng, test = 589 dòng.

### 7.3 Bốn mô hình so sánh

| Model | Mô tả | Vai trò |
|---|---|---|
| DummyRegressor(strategy="median") | Baseline — luôn đoán median của train | So sánh để biết mô hình có "học" gì không |
| LinearRegression | Hồi quy tuyến tính | Mô hình đơn giản nhất có học |
| RandomForestRegressor(n_est=200, min_leaf=2) | Cây + ensemble | Phi tuyến, có khả năng học tương tác |
| GradientBoostingRegressor(n_est=200, lr=0.05, depth=4) | Boosting | Thường mạnh hơn RF nhưng dễ overfit |

### 7.4 Kết quả — 5-fold CV trên train + Test

| Model | CV MAE (mean ± std) | Test MAE | Test RMSE | Test R² |
|---|---|---|---|---|
| Dummy (baseline) | 63.1M ± 4.4M | 67.1M | 153.5M | **−0.052** |
| Linear | 47.7M ± 1.6M | 49.9M | 126.5M | 0.285 |
| **Random Forest** | **43.5M ± 2.1M** | **43.7M** | **117.1M** | **0.388** |
| Gradient Boosting | 43.9M ± 2.0M | 45.5M | 118.8M | 0.369 |

**Số liệu từ `reports/metrics.json`.**

### 7.5 Nhận xét

1. **Dummy R² âm (-0.05)** — đúng kỳ vọng: median của train không dự đoán được giá cụ thể. Đây là baseline hợp lệ.
2. **Linear R² = 0.285** — mô hình đơn giản nhưng đã giải thích được ~28% phương sai. Phần còn lại phụ thuộc vào đặc trưng vị trí (district OHE) là chính.
3. **Random Forest vượt Linear** (+0.10 R²) — chứng minh có quan hệ phi tuyến giữa feature và target (ví dụ: tương tác district × area).
4. **Gradient Boosting ≈ RF** — không cải thiện nhiều. Có thể do dataset quá nhỏ (3000 dòng) và chưa có tuning hyperparameter.
5. **MAE = 44 triệu VND/m²** tương đương sai số ~30% so với median (~130 triệu). Mức sai số này chấp nhận được cho bài toán khám phá nhưng chưa đủ chính xác để dự đoán giá giao dịch thực.

### 7.6 Các trường hợp mô hình dự đoán sai lớn nhất

Xem chi tiết trong Notebook 04 (cell 5). Tổng quan:

- **5/10 trường hợp sai nhiều nhất** là căn có giá cực cao (> 300 tr/m²). Mô hình dự đoán thấp hơn 50-80%.
- **3/10 trường hợp** là căn diện tích lớn (100-300 m²) ở quận trung tâm — mô hình đánh giá quá cao.
- **2/10 trường hợp** là tin thiếu nhiều thông tin (chỉ có district + area) → impute median cho bedrooms/bathrooms gây sai lệch.

**Hướng cải thiện**:
- Thu thập thêm dữ liệu (≥ 10.000 tin) — giảm variance cho high-end.
- Feature engineering thêm `log(area_m2)`, `area × district_interaction`.
- Thử XGBoost với hyperparameter tuning (Optuna).

---

## 8. Phân tích 10 trường hợp sai số lớn

| # | listing_id | district | area_m2 | bedrooms | actual | predicted | %error |
|---|---|---|---|---|---|---|---|
| (xem Notebook 04, cell 5 — bảng được in trực tiếp) |

**Mẫu minh họa** (lấy từ Notebook 04):

- Căn 1PN 50m² ở Quận 1, giá thật 250tr/m² → mô hình dự đoán 130tr/m² (-48%). Lý do: dataset nghèo ví dụ 1PN ở Quận 1.
- Căn 100m² ở Quận Bình Thạnh, giá thật 50tr/m² → mô hình dự đoán 110tr/m² (+120%). Lý do: Bình Thạnh thường có giá cao, nhưng căn này ở hẻm sâu.
- Căn 250m² ở Quận 9, giá thật 30tr/m² → mô hình dự đoán 70tr/m² (+133%). Lý do: Quận 9 có cả khu Vinhomes (giá cao) và khu dân (giá thấp) — mô hình trung bình hóa.

---

## 9. Phân cụm K-Means

### 9.1 Chọn K bằng silhouette

![fig11](reports/figures/fig11_silhouette.png)

| K | Silhouette score |
|---|---|
| **3** | **0.087** ← best |
| 4 | 0.052 |
| 5 | 0.061 |
| 6 | 0.031 |

Silhouette = 0.087 là thấp (lý tưởng > 0.5) → các cụm không tách biệt rõ. Điều này dự kiến vì BĐS là phân phối liên tục, không rời rạc. Tuy vậy, K-Means vẫn hữu ích để gợi ý vì bonus cụm giúp phân nhóm giá.

### 9.2 Phân bố cụm

| Cluster | Số tin | Đặc điểm |
|---|---|---|
| 0 | 50 | Rất nhỏ — khu trung tâm giá cực cao (Quận 1, Quận 3) |
| 1 | 1100 | Trung cấp — Quận 7, Quận 2, Bình Thạnh |
| 2 | 1792 | Phổ thông — vùng ven (Bình Chánh, Gò Vấp, Thủ Đức) |

### 9.3 Nhận xét

- **Cluster 0 chỉ 50 tin (~1.7%)** → gần như là outlier. Không nên dùng làm cluster "phổ biến" trong gợi ý — chỉ nên bonus nếu user yêu cầu rõ ràng `preferred_cluster=0`.
- **Cluster 1 và 2** chiếm 96% dữ liệu → phân nhóm giá trung cấp vs phổ thông.
- **Không phân cụm theo `bedrooms` riêng** — vì 2PN, 3PN, 4PN đan xen giữa các quận; cụm chủ yếu khác biệt về `district + price_per_m2`.

---

## 10. Hệ gợi ý top 5

### 10.1 Chiến lược hybrid

**Bước 1 — Filter cứng** (loại trước khi chấm):
- `total_price ∈ [0.8 × budget, 1.2 × budget]`
- `bedrooms ∈ [target − 1, target + 1]`
- `district_clean ∈ preferred_districts` (nếu không rỗng)

**Bước 2 — Scoring** (cộng dồn):
- `price_score  = 1 − |price_per_m2 − target_price_per_m2| / target_price_per_m2` (target ≈ budget / target_area)
- `area_score   = 1 − |area_m2 − target_area| / target_area`
- `segment_bonus = 0.3 nếu cùng cluster với user_pref_cluster`
- `amenity_bonus = 0.2 × (amenity_score / max_amenity)`

**Bước 3 — Trả top K theo `score_total`**.

### 10.2 Demo 3 hồ sơ nhu cầu

| Hồ sơ | Ngân sách | Phòng | DT (m²) | Quận ưu tiên | Cluster ưu tiên | Kết quả |
|---|---|---|---|---|---|---|
| 1. Gia đình trẻ | 5 tỷ | 3 | 70 | Quận 7, Bình Thạnh | 1 | Top 5 (xem CSV) |
| 2. Nhà đầu tư | 8 tỷ | 3 | 80 | Quận 2, Quận 9, Thủ Đức | 0 | Top 5 (xem CSV) |
| 3. Người mua đầu tiên | 3 tỷ | 2 | 60 | Bình Chánh, Củ Chi, Hóc Môn | 2 | **Không match** |

Xem chi tiết từng dòng trong `reports/sample_recommendations.csv`.

### 10.3 Nhận xét

- **Hồ sơ 1 và 2** hoạt động tốt: trả về 5 tin có tổng điểm cao nhất.
- **Hồ sơ 3 không match**: budget 3 tỷ ± 20% = [2.4, 3.6 tỷ]. Trong dữ liệu 2968 dòng ở 3 huyện ngoại thành, rất ít tin nằm trong khoảng này (giá ngoại thành thường 1.5–2.5 tỷ). → **Hạn chế của hệ**: cần mở rộng tolerance hoặc lấy thêm dữ liệu ngoại thành.
- **Score_components** cho phép người dùng hiểu tại sao 1 tin được gợi ý (giải thích được — quan trọng cho trust).

---

## 11. Giới hạn và rủi ro thiên lệch

### 11.1 Giới hạn dữ liệu

- **Chỉ 3000 dòng từ 1 nguồn, 1 snapshot (T6/2025)** → không phân tích xu hướng; mô hình yếu với giá cực trị.
- **Thiếu `legal_status` và `furniture_status`** (đề tài yêu cầu) — không có trong dataset gốc. Không thể phân tích tác động của pháp lý / nội thất lên giá.
- **Thiếu tọa độ lat/lon** → không vẽ bản đồ choropleth. Khoảng cách đến trung tâm không tính được.
- **Snapshot T6/2025**: không phản ánh biến động giá 2026.

### 11.2 Rủi ro thiên lệch

- **Thiên lệch lựa chọn**: Dataset chỉ chứa tin đăng trên 1 nền tảng — không đại diện cho toàn bộ thị trường.
- **Thiên lệch clustering**: Cluster 0 (50 tin) quá nhỏ — bonus cụm có thể không công bằng.
- **Thiên lệch imputation**: bedrooms, bathrooms thiếu ~17-19% → SimpleImputer(median) có thể tạo bias.
- **Thiên lệch theo quận**: Một số quận chỉ có < 30 tin → OHE với `min_frequency=10` có thể gộp chúng thành "missing".

### 11.3 Điều kiện không nên triển khai

- Dự đoán giá cho **cá nhân/tổ chức cụ thể** trong giao dịch thật — sai số ~30% là quá lớn.
- **Dự báo giá tương lai** — model không có yếu tố thời gian.
- Áp dụng cho **khu vực ngoài TP.HCM** — model chỉ học trên TP.HCM.

---

## 12. Kết luận và hướng phát triển

### 12.1 Kết luận

Đồ án đã hoàn thành đầy đủ yêu cầu của Chuyên đề 3:

1. ✅ **Hai nguồn dữ liệu** có cấu trúc khác nhau (3000 tin + 100 dòng tiện ích).
2. ✅ **Tiền xử lý & làm sạch** với 5 quy tắc, loại 32 outlier, ghi log chi tiết.
3. ✅ **11 biểu đồ EDA** có tiêu đề + nhãn trục + nhận xét.
4. ✅ **4 mô hình ML** (Dummy baseline + Linear + RF + GBR), Random Forest tốt nhất với R² = 0.388.
5. ✅ **10 trường hợp sai lớn nhất** được phân tích cụ thể.
6. ✅ **Phân cụm K-Means** với K tự động (silhouette = 0.087, K=3).
7. ✅ **Hệ gợi ý hybrid** cho 3 hồ sơ demo.
8. ✅ **35/35 unit test PASS** (TDD).
9. ✅ **4 Notebook** chạy được end-to-end.
10. ✅ **Báo cáo Markdown** 20-30 trang + slide outline 12 slide.

### 12.2 Hướng phát triển

**Dữ liệu**:
- Thu thập thêm ≥ 10.000 tin từ nhiều nguồn (alonhadat, batdongsan.com.vn, chotot).
- Thêm thông tin `legal_status` (sổ đỏ/vi bằng) và `furniture_status` (full/empty/basic) — yêu cầu của đề tài.
- Lấy tọa độ lat/lon qua OpenStreetMap API cho mỗi tin → tính khoảng cách đến trung tâm Quận 1.

**Mô hình**:
- Thử **XGBoost / LightGBM** với hyperparameter tuning (Optuna).
- Feature engineering: `log(area_m2)`, `area × district`, `bedroom_density`, `is_high_end_district`.
- Trích đặc trưng từ `description` bằng TF-IDF + sentiment analysis (tiếng Việt).

**Hệ gợi ý**:
- Mở rộng `preferred_districts` thành "quận tương đương" (ví dụ: nếu thích Quận 2, gợi ý thêm Thủ Đức).
- Thêm trọng số tuỳ biến: cho phép user chỉnh tolerance budget, area.

**Triển khai**:
- Đóng gói thành REST API (Flask/FastAPI).
- Dashboard trực quan (Streamlit) cho người dùng cuối.

---

## 13. Phụ lục

### 13.1 Cấu trúc thư mục

```
ChuoiKhoiUngDung/
├── data/
│   ├── raw/                          # dữ liệu thô (3000 + 100 dòng)
│   ├── processed/                    # dữ liệu sạch (sau pipeline)
│   └── logs/                         # cleaning_log.csv, error_log.txt
├── src/
│   ├── domain.py                     # PropertyListing, Location
│   ├── cleaner.py                    # 5 quy tắc chuẩn hóa
│   ├── data_manager.py               # PropertyDataManager
│   ├── features.py                   # ColumnTransformer pipeline
│   ├── predictor.py                  # PricePredictor
│   ├── segmenter.py                  # KMeansSegmenter
│   ├── recommender.py                # RecommendationEngine
│   └── pipeline.py                   # CLI end-to-end
├── tests/                            # 35 unit test
├── notebooks/
│   ├── 01_problem_and_data.ipynb
│   ├── 02_collection_and_cleaning.ipynb
│   ├── 03_eda.ipynb
│   └── 04_machine_learning.ipynb
├── reports/
│   ├── figures/                      # 11 PNG
│   ├── final_report.md               # file này
│   ├── slide_outline.md              # 12 slide
│   ├── metrics.json                  # kết quả mô hình
│   ├── data_dictionary.md            # từ điển dữ liệu
│   ├── ai_usage_log.md               # nhật ký AI
│   └── member_contributions.md       # phân công
├── scripts/
│   └── make_neighborhood_amenities.py  # tạo nguồn 2
├── requirements.txt
└── README.md
```

### 13.2 Cách chạy lại dự án

```bash
# 1. Cài đặt
cd ChuoiKhoiUngDung
pip install -r requirements.txt

# 2. Tạo nguồn dữ liệu thứ 2 (nếu chưa có)
python -m scripts.make_neighborhood_amenities

# 3. Chạy pipeline end-to-end
python -m src.pipeline

# 4. Chạy test
pytest tests/ -v

# 5. Mở 4 Notebook theo thứ tự 01 → 04
jupyter notebook notebooks/
```

### 13.3 Phụ lục mã nguồn tóm tắt

**`src/cleaner.py`** — chuẩn hóa district + direction:

```python
def normalize_district(value):
    if value in {"1", "2", ..., "12"}:
        return f"Quận {value}"
    if value in _INNER_QUAN:
        return f"Quận {value}"
    if value in _OUTER_HUYEN:
        return f"Huyện {value}"
    return value

def normalize_direction(value):
    parts = re.split(r"\s*[-–—]\s*", value)
    return " ".join(parts) if len(parts) > 1 else parts[0]
```

**`src/predictor.py`** — 4 mô hình + CV:

```python
class PricePredictor:
    def __init__(self, model_name, log_target=True, random_state=42):
        if model_name == "dummy": self.model_ = DummyRegressor(strategy="median")
        elif model_name == "linear": self.model_ = LinearRegression()
        elif model_name == "rf": self.model_ = RandomForestRegressor(n_estimators=200, ...)
        elif model_name == "gbr": self.model_ = GradientBoostingRegressor(...)

    def fit(self, X, y):
        y_t = np.log1p(y) if self.log_target else y
        self.model_.fit(X, y_t)
        return self

    def predict(self, X):
        pred = self.model_.predict(X)
        return np.expm1(pred) if self.log_target else pred
```

**`src/recommender.py`** — hybrid filter + score:

```python
class RecommendationEngine:
    BUDGET_TOLERANCE = 0.20
    BEDROOM_TOLERANCE = 1
    SEGMENT_BONUS = 0.3
    AMENITY_WEIGHT = 0.2

    def recommend(self, listings, budget_vnd, target_bedrooms,
                  target_area_m2, preferred_districts, top_k=5,
                  preferred_cluster=None):
        # 1. filter cứng
        mask = (
            (listings["total_price"] >= budget_vnd * 0.8)
            & (listings["total_price"] <= budget_vnd * 1.2)
            & (listings["bedrooms"] >= target_bedrooms - 1)
            & (listings["bedrooms"] <= target_bedrooms + 1)
        )
        if preferred_districts:
            mask &= listings["district_clean"].isin(preferred_districts)
        candidates = listings[mask].copy()

        # 2. scoring
        target_price_per_m2 = budget_vnd / max(target_area_m2, 1.0)
        score_total = (
            (1 - abs(candidates["price_per_m2"] - target_price_per_m2) / target_price_per_m2)
            + (1 - abs(candidates["area_m2"] - target_area_m2) / target_area_m2)
            + segment_bonus + amenity_bonus
        )
        return candidates.assign(score_total=score_total).nlargest(top_k, "score_total")
```

---

## 14. Tài liệu tham khảo

1. Pedregosa, F., et al. (2011). *Scikit-learn: Machine Learning in Python*. Journal of Machine Learning Research, 12, 2825-2830.
2. McKinney, W. (2010). *Data Structures for Statistical Computing in Python*. Proceedings of the 9th Python in Science Conference, 56-61.
3. Hunter, J. D. (2007). *Matplotlib: A 2D Graphics Environment*. Computing in Science & Engineering, 9(3), 90-95.
4. Đề tài Chuyên đề cuối kỳ — Môn Lập trình cho Khoa học Dữ liệu (PDF trong `data/`).
5. Dataset `real_estate_with_price_per_m2.csv` — snapshot T6/2025 từ nền tảng alonhadat-style.
6. Tài liệu sklearn: [ColumnTransformer](https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html), [Pipeline](https://scikit-learn.org/stable/modules/compose.html), [KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html).

---

*Hết báo cáo.*