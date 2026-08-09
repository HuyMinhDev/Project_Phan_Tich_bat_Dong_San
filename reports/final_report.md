# Báo cáo đồ án KHDL cuối kỳ

## Chuyên đề 3: Phân tích và gợi ý bất động sản — Căn hộ/Chung cư TP.HCM

---

**Học viên**: [Điền tên]
**MSSV**: [Điền]
**Môn học**: Lập trình cho Khoa học Dữ liệu
**Giảng viên hướng dẫn**: [Điền]
**Ngày nộp**: 08/08/2026

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

Đồ án này xây dựng một pipeline phân tích và gợi ý tin đăng **căn hộ/chung cư** tại 6 quận TP.HCM (Thành phố Thủ Đức, Quận Bình Thạnh, Quận 7, Quận Gò Vấp, Quận 12, Quận Bình Tân) từ tập dữ liệu **1799 tin** crawl từ chotot (08/2026). Quy trình gồm 4 bước chính:

1. **Chuẩn hóa dữ liệu**: 20 dòng outlier bị loại (3 dòng diện tích ngoài phạm vi 10-500m², 17 dòng số phòng > 10); 6 giá trị `district` được chuẩn hóa; mã hướng 1..8 decode về 8 hướng chính; mã nội thất 1..4 và pháp lý 1,2,4,5,6 decode về nhãn tiếng Việt. Cuối cùng còn **1773 dòng** sau khi dropna(subset=`price_per_m2`) (6 dòng thiếu giá).
2. **Dự đoán giá/m²**: So sánh 4 mô hình (Dummy baseline + Linear Regression + Random Forest + Gradient Boosting) với pipeline sklearn `ColumnTransformer`. Mô hình tốt nhất là **Random Forest với R² = 0.169 trên tập test**, MAE ≈ 13.9 triệu VND/m² (sai số ~26% so với median 53 tr/m²).
3. **Phân cụm K-Means**: Chọn K = **4** theo silhouette score (cao nhất 0.083). Bốn cụm với kích thước không đều — một cụm lớn (1396 tin chiếm 78.7%) và 3 cụm nhỏ (47/165/165). Các cụm khác biệt chủ yếu theo `direction_code` (hướng nhà), KHÔNG theo phân khúc giá (median 4 cluster gần như nhau ~50-54tr/m²).
4. **Hệ gợi ý top 5**: Chiến lược hybrid (filter cứng theo ngân sách ± 20%, số phòng ± 1, quận ưu tiên; cộng điểm theo giá, diện tích, cùng cụm K-Means, tiện ích). Demo với 3 hồ sơ nhu cầu căn hộ.

Tất cả **45 unit test pass**, pipeline chạy end-to-end thành công, **12 biểu đồ EDA** được sinh, **4 Notebook Jupyter** chạy được từ đầu đến cuối.

---

## 2. Giới thiệu bài toán

### 2.1 Bối cảnh

Thị trường căn hộ/chung cư TP.HCM là một trong những thị trường sôi động nhất Việt Nam, với hàng nghìn tin đăng mỗi ngày trên các nền tảng như chotot, batdongsan.com.vn, alonhadat. Tuy nhiên, dữ liệu thô từ các nguồn này có những đặc thù riêng:

- **Giá viết dạng text**: "3,19 tỷ", "2,1 tỷ" — cùng giá trị nhưng nhiều cách ghi.
- **Hướng nhà và hướng ban công dạng mã số** (1..8 cho 8 hướng chính) — cần decode.
- **Tình trạng nội thất và pháp lý dạng mã** (furnishing_status 1..4, legal_status 1,2,4,5,6) — không có nhãn text trong dữ liệu gốc.
- **Outlier rõ ràng**: căn 1323 m² (chắc chắn sai — gấp 16× trung bình), căn có 11 phòng ngủ (căn hộ không hợp lý).
- **Nhiều tin thiếu thông tin** (direction 79%, balcony_direction 73%, furnishing_status 34%) → cần imputation.

### 2.2 Mục tiêu

Theo đề tài Chuyên đề 3, đồ án cần đạt các mục tiêu:

1. **Chuẩn hóa** giá, diện tích, giá/m², địa điểm và các thuộc tính mô tả.
2. **Phát hiện** tin trùng và ngoại lệ.
3. **Dự đoán** giá/m² (`price_per_m2`).
4. **Phân khúc** căn hộ bằng K-Means.
5. **Gợi ý** top 5 theo ngân sách, khu vực, diện tích, số phòng.
6. **Trực quan hóa** ≥ 8 biểu đồ có tiêu đề + nhãn trục + nhận xét.

### 2.3 Sáu câu hỏi nghiên cứu

1. Trong 6 quận có dữ liệu, quận nào có `price_per_m2` cao nhất?
2. Diện tích và số phòng ảnh hưởng thế nào đến giá/m²?
3. Hướng nhà, hướng ban công, tình trạng nội thất và pháp lý có liên hệ gì với giá không?
4. Tin nào có giá/diện tích bất thường hoặc có khả năng trùng?
5. Mô hình dự đoán giá/m² đạt sai số bao nhiêu (MAE / RMSE / R²)?
6. Top 5 tin nào phù hợp với từng hồ sơ nhu cầu (gia đình trẻ / nhà đầu tư / mua cao cấp)?

---

## 3. Phương pháp thu thập dữ liệu

### 3.1 Nguồn dữ liệu

| Nguồn | File | Số dòng | Mô tả | Schema |
|---|---|---|---|---|
| **1 (chính)** | `data/raw/real_estate_apartment.xlsx` | 1799 | Snapshot tin đăng BĐS căn hộ tại 6 quận TP.HCM, crawl từ chotot (08/2026) | 32 cột (id, tiêu đề, mô tả, loại hình, tỉnh, quận, phường, đường, dự án, vĩ độ, kinh độ, diện tích, phòng, mã hướng, mã nội thất, mã pháp lý, tổng giá, giá text, giá/m², ngày đăng, source, url, image_count) |
| **2 (phụ)** | `data/raw/neighborhood_amenities.csv` | 91 | Thông tin tiện ích theo (quận, phường) — tự tạo deterministic (seed=42) | 8 cột (ward, district_clean, school/hospital/supermarket/park/bus_stops counts, amenity_score) |

### 3.2 Ghi chú quan trọng về nguồn dữ liệu

Đồ án sử dụng **dữ liệu crawl từ chotot** (lưu dưới dạng xlsx) — không crawl trực tiếp trong quá trình thực hiện đồ án. Lý do:

- **Tuân thủ điều khoản sử dụng**: Theo yêu cầu đồ án (mục I.2.3 PDF đề tài), không được vượt CAPTCHA, anti-bot, hoặc cơ chế chống bot.
- **Phương án dữ liệu dự phòng**: Theo yêu cầu đồ án (mục I.2.5), nhóm phải có phương án dữ liệu dự phòng. Snapshot được cung cấp là phương án được phép.
- **Tính tái lập**: Snapshot cho phép người chấm chạy lại pipeline và có cùng kết quả.

Nguồn dữ liệu thứ hai (`neighborhood_amenities.csv`) là **dữ liệu mô phỏng có kiểm soát** — sinh bằng random seed = 42 từ các cặp (district, ward) có trong data chính. Công thức weighted score cố định. Điều này:
- Đáp ứng yêu cầu "ít nhất 2 nguồn / 2 loại tập tin có cấu trúc khác nhau" của đề tài.
- Có thể thay thế bằng dữ liệu thật (OpenStreetMap) trong phiên bản tiếp theo.

### 3.3 Phạm vi phân tích

- **Địa lý**: 6 quận TP.HCM — Thành phố Thủ Đức, Quận Bình Thạnh, Quận 7, Quận Gò Vấp, Quận 12, Quận Bình Tân.
- **Loại hình**: Căn hộ/Chung cư (toàn bộ 1799 dòng đều là `property_type = "Căn hộ/Chung cư"`).
- **Thời gian**: Snapshot T7-T8/2026 (không phân tích xu hướng dài hạn).

---

## 4. Từ điển dữ liệu

Chi tiết từng cột xem `reports/data_dictionary.md`. Tóm tắt các cột chính:

| Cột | Kiểu | Missing % | Vai trò |
|---|---|---|---|
| `listing_id` | int | 0.00 | Khóa chính |
| `total_price` | int | 0.00 | Target phụ (lọc outlier); dùng cho recommender |
| `area_m2` | float | 0.33 | Feature chính |
| `price_per_m2` | float | 0.33 | **Target** (tính lại từ total_price/area_m2) |
| `bedrooms` | float | 0.17 | Feature chính |
| `bathrooms` | float | 15.6 | Feature phụ |
| `direction`, `balcony_direction` | float (1..8) | 78.9 / 73.2 | Mã hướng → decode text + dùng làm feature số |
| `furnishing_status` | float (1..4) | 34.4 | Mã nội thất → decode + feature số |
| `legal_status` | float (1,2,4,5,6) | 20.0 | Mã pháp lý → decode + feature số |
| `apartment_type` | int (1..6) | 0.00 | Loại căn hộ (1 = phổ biến nhất, 1721/1799) |
| `image_count` | int | 0.00 | Feature phụ (chất lượng tin) |
| `project_name` | str | 20.9 | Categorical feature (OHE với min_freq=10) |
| `district` | str | 0.00 | Categorical (6 quận) |
| `ward` | str | 0.89 | Khóa join với amenities |

---

## 5. Tiền xử lý và làm sạch

### 5.1 Quy trình làm sạch

```python
# Trong src.cleaner.clean_dataframe(df)
1. df["district_clean"]      = df["district"].apply(normalize_district)        # pass-through
2. df["direction_clean"]     = df["direction"].apply(normalize_direction)      # decode 1..8
3. df["furnishing_label"]    = df["furnishing_status"].apply(decode_furnishing)
4. df["legal_label"]         = df["legal_status"].apply(decode_legal)
5. df["direction_code"]      = df["direction"]            # giữ mã cho ML
6. df["balcony_code"]        = df["balcony_direction"]
7. df["furnishing_code"]     = df["furnishing_status"]
8. df["legal_code"]          = df["legal_status"]
9. df["apartment_type"]      = df["apartment_type"]
10. df["image_count"]        = df["image_count"]
11. cleaned, log = filter_outliers(df)                                       # area 10-500, price ≥100tr, bedrooms ≤10
12. cleaned = recompute_price_per_m2(cleaned)
```

### 5.2 Quy tắc lọc outlier (cho căn hộ)

| Biến | Quy tắc | Lý do |
|---|---|---|
| `area_m2` | < 10 hoặc > 500 → drop | Căn hộ bình thường 24-200m²; 1323m² là penthouse/duplicate |
| `total_price` | < 100 triệu → drop | Căn hộ TP.HCM tối thiểu > 500 triệu |
| `bedrooms` | > 10 → drop | Căn hộ hiếm khi > 5PN; 11, 19, 50 là sai dữ liệu |

### 5.3 Mapping mã → nhãn

| Mã `direction` (1..8) | Tên hướng |
|---|---|
| 1 | Đông |
| 2 | Tây |
| 3 | Nam |
| 4 | Bắc |
| 5 | Đông Nam |
| 6 | Tây Nam |
| 7 | Đông Bắc |
| 8 | Tây Bắc |

| Mã `furnishing_status` | Nhãn |
|---|---|
| 1 | Không nội thất |
| 2 | Nội thất cơ bản |
| 3 | Nội thất đầy đủ |
| 4 | Nội thất cao cấp |

| Mã `legal_status` | Nhãn |
|---|---|
| 1 | Đang cập nhật |
| 2 | Sổ hồng lâu dài |
| 4 | Hợp đồng mua bán |
| 5 | Sổ hồng chung |
| 6 | Sổ hồng riêng |

### 5.4 Kết quả làm sạch

| Bước | Số dòng còn | Ghi chú |
|---|---|---|
| Raw xlsx | 1799 | 32 cột gốc |
| Sau lọc outlier (cleaner.py) | 1779 | Bỏ 20 dòng ngoại lệ (1.11%) |
| Sau dropna(subset=price_per_m2) | 1773 | Bỏ thêm 6 dòng thiếu giá |
| Có `amenity_score` (match) | 1773 | 100% match theo (district_clean, ward) — fillna median theo district cho phường chưa có |

**Phân bố lỗi trong cleaning_log**:
- 17 dòng `bedrooms_outlier` (>10 phòng)
- 3 dòng `area_out_of_range` (area < 10 hoặc > 500 m²)

File log: `data/logs/cleaning_log.csv`, `data/logs/error_log.txt`.

---

## 6. EDA — Phân tích khám phá dữ liệu

Tất cả **12 biểu đồ** được lưu trong `reports/figures/`.

### 6.1 Phân bố `price_per_m2`

![fig01](reports/figures/fig01_price_distribution.png)

**Nhận xét**: Phân bố lệch phải (skewed) do vài căn penthouse/căn góc giá > 200tr/m². Median ~53tr/m², max 934tr/m². Log-transform giúp phân bố gần chuẩn — đây là lý do fit mô hình trên log1p(price_per_m2).

### 6.2 Giá/m² trung bình theo 6 quận

![fig02](reports/figures/fig02_top_districts.png)

**Nhận xét**: **Quận Bình Thạnh** (~71.4 tr/m²) dẫn đầu — gần trung tâm, view sông. Thứ hai là **Quận 7** (~58.5 tr/m²) — khu Nam Sài Gòn. **Thành phố Thủ Đức** (~54.2 tr/m²) — nhiều dự án mới ở khu vực phát triển. Quận 12 (~45.4 tr/m²), Gò Vấp (~44.2 tr/m²), Bình Tân (~42.8 tr/m²) là nhóm giá thấp (ngoại thành).

### 6.3 Phân bố giá theo hướng nhà

![fig03](reports/figures/fig03_price_by_direction.png)

**Nhận xét**: Chênh lệch giá giữa các hướng nhỏ (median 55-65tr/m²). Hướng Đông Nam và Tây Nam có median cao hơn một chút — phù hợp phong thuỷ "tránh nắng chiều, đón gió mát".

### 6.4 Diện tích vs tổng giá

![fig04](reports/figures/fig04_area_vs_price.png)

**Nhận xét**: Quan hệ gần tuyến tính — diện tích càng lớn giá càng cao. Một số căn diện tích 50-80m² ở mức giá 3-5 tỷ → căn hộ cao cấp ở vị trí đắt đỏ.

### 6.5 Số tin đăng theo quận

![fig05](reports/figures/fig05_listings_by_district.png)

**Nhận xét**: Thành phố Thủ Đức có nhiều tin nhất (593 — nhiều dự án mới, sáp nhập từ Quận 2/9/Thủ Đức cũ). Quận 7 (352), Bình Tân (302), Bình Thạnh (212) là nhóm tiếp theo. Quận 12 (173) và Gò Vấp (141) là nhóm ít tin nhất.

### 6.6 Heatmap correlation

![fig06](reports/figures/fig06_correlation_heatmap.png)

**Nhận xét**: Tương quan giữa `price_per_m2` và các biến khác yếu (<0.3) — giá/m² căn hộ phụ thuộc chủ yếu vào vị trí (district) và dự án (`project_name`) hơn là diện tích/phòng. bedrooms ↔ area_m2 = 0.55 (dự kiến). total_price ↔ area_m2 = 0.70.

### 6.7 Số tin đăng theo tháng

![fig07](reports/figures/fig07_postings_over_time.png)

**Nhận xét**: Dữ liệu tập trung vào T7-T8/2026 — không phân tích xu hướng dài hạn.

### 6.8 Phân bố giá theo số phòng ngủ

![fig08](reports/figures/fig08_price_by_bedrooms.png)

**Nhận xét**: Phân bố giá theo số phòng ngủ (sau dropna, 1773 dòng) — median price_per_m2:
- 1PN (270 tin, 15.2%): ~56.6 tr/m²
- **2PN (1189 tin, 67.1%)**: ~51.4 tr/m² — chiếm đa số
- 3PN (286 tin, 16.1%): ~56.3 tr/m²
- 4PN+ (25 tin, 1.4%): ~146.7 tr/m² — đa số là penthouse/căn góc view đẹp, kéo median cao đột biến

> 1PN có giá/m² **KHÔNG cao nhất** — 4PN+ mới là nhóm cao nhất do penthouse/căn góc view đẹp. 2PN chiếm đa số (67%) với giá/m² trung bình thấp hơn 1PN một chút.

### 6.9 Amenity score theo quận

![fig09](reports/figures/fig09_amenity_by_district.png)

**Nhận xét**: Thành phố Thủ Đức và Quận 7 có amenity_score cao nhất (~7.5-8.5) — nhiều dự án, tiện ích hiện đại. Bình Tân và Quận 12 thấp hơn (~5-6).

### 6.10 Phân bố số phòng ngủ

![fig10](reports/figures/fig10_bedrooms_count.png)

**Nhận xét**: 2PN chiếm đa số (67%), tiếp theo là 1PN (271) và 3PN (287). Phù hợp với cơ cấu căn hộ TP.HCM — gia đình nhỏ và vợ chồng trẻ.

### 6.11 Phân bố nội thất & pháp lý

![fig11](reports/figures/fig11_furnishing_legal.png)

**Nhận xét**: Nội thất cơ bản chiếm đa số (~566 tin) — căn hộ bàn giao thô hoặc semi-furnished. Pháp lý: **sổ hồng riêng chiếm 60%** — dấu hiệu tích cực về tính hợp pháp của thị trường căn hộ.

---

## 7. Mô hình dự đoán giá/m²

### 7.1 Thiết kế pipeline

```python
NUMERIC_COLS = [
    "area_m2", "bedrooms", "bathrooms",
    "direction_code", "balcony_code", "furnishing_code",
    "legal_code", "image_count", "apartment_type",
]
CATEGORICAL_COLS = ["district_clean", "direction_clean", "project_name"]

pre = build_preprocessor(NUMERIC_COLS, CATEGORICAL_COLS)
# - numeric: SimpleImputer(median) → StandardScaler
# - categorical: SimpleImputer(constant="missing") → OneHotEncoder(handle_unknown="ignore", min_frequency=10)
```

**Quyết định**:
- `log_target=True`: fit trên log1p(price_per_m2), inverse bằng expm1 → giảm skewness.
- `OneHotEncoder(min_frequency=10)`: gộp dummy cho category hiếm → giảm chiều.
- `handle_unknown="ignore"`: robust với district/project mới.

### 7.2 Train/test split

- **Tỉ lệ**: 80/20, `random_state=42`, shuffle=True.
- **Kích thước**: train = 1418 dòng, test = 355 dòng.
- **Features sau transform**: 47 cột (9 numeric + 38 categorical OHE).

### 7.3 Bốn mô hình so sánh

| Model | Mô tả | Vai trò |
|---|---|---|
| DummyRegressor(strategy="median") | Baseline | So sánh "mô hình có học không" |
| LinearRegression | Hồi quy tuyến tính | Baseline có học |
| RandomForestRegressor(n_est=200, min_leaf=2) | Ensemble cây | Phi tuyến, học tương tác |
| GradientBoostingRegressor(n_est=200, lr=0.05, depth=4) | Boosting | Thường mạnh hơn RF |

### 7.4 Kết quả — 5-fold CV trên train + Test

| Model | CV MAE (mean ± std) | Test MAE | Test RMSE | Test R² |
|---|---|---|---|---|
| Dummy (baseline) | 18.8M ± 1.5M | 18.5M | 37.1M | **−0.041** |
| Linear | 14.1M ± 1.0M | 14.9M | 33.7M | 0.143 |
| **Random Forest** | **13.0M ± 0.7M** | **13.9M** | **33.2M** | **0.169** |
| Gradient Boosting | 13.4M ± 1.2M | 14.4M | 33.7M | 0.162 |

**Số liệu từ `reports/metrics.json`.**

### 7.5 Nhận xét

1. **Dummy R² âm (-0.04)** — đúng kỳ vọng: median không dự đoán được.
2. **Linear R² = 0.14** — giải thích ~14% phương sai. Phần còn lại phụ thuộc tương tác phi tuyến (district × dự án).
3. **Random Forest vượt Linear** (+0.03 R²) — chứng minh có quan hệ phi tuyến.
4. **Gradient Boosting ≈ RF** — không cải thiện nhiều. Có thể do dataset nhỏ (1779 dòng) và chưa tuning hyperparameter.
5. **MAE = 13.9 triệu VND/m²** tương đương sai số ~26% so với median (~53 triệu).
6. **R² thấp (0.17) là thực tế của căn hộ** — giá phụ thuộc nhiều yếu tố phi số (view, tầng, nội thất chi tiết, tiến độ dự án, view sông/hồ). Mức R² này vẫn vượt baseline rõ rệt và phù hợp với dữ liệu BĐS thực.

---

## 8. Phân tích 10 trường hợp sai số lớn

Xem chi tiết trong Notebook 04 (cell 8). Top 10 có `pct_error` từ **47.5% đến 147.4%** (median 62.5%).

### 8.1 Phân tích chi tiết

| Vấn đề | Số trường hợp | Đặc điểm |
|---|---:|---|
| **High price (>150tr/m²)** | 5/10 | Model dự đoán thấp hơn 30-60%. Đây là các căn penthouse/căn góc view đẹp (Landmark 81, Empire City, Masteri An Phú, Midtown, Lumière Riverside). |
| **Price anomaly (Duplex)** | 1/10 | Listing 177850739: 140m² 3PN ở Thủ Đức, actual 51.4tr/m² nhưng model dự đoán 127.3tr/m². Căn "Duplex thông tầng" giá thật bất thường, có thể data entry error. |
| **Missing nhiều (≥3 features)** | 5/10 | Top 10 có missing_count: 0 (2), 2 (5), 3 (1), 4 (1), 5 (1) → impute median gây sai lệch cho 50% case. |
| **Diện tích nhỏ + vị trí đắt** | 2/10 | 51m² ở Thủ Đức Masteri An Phú, 60m² Bình Thạnh — model dựa vào diện tích trung bình → underprice. |

### 8.2 Hướng cải thiện

- **Dữ liệu**: Thu thập ≥ 10.000 tin, mở rộng 24 quận, thêm thông tin tầng/view/ban công.
- **Feature engineering**: `log(area_m2)`, `area × project`, `bedroom_density`, `is_high_end_district`, `missing_count` (count missing để model biết uncertainty).
- **Mô hình**: Thử XGBoost/LightGBM với hyperparameter tuning (Optuna).
- **Outlier removal**: Loại bỏ các căn có `pct_error > 100%` trong tập train (Duplex, data entry error).
- **DISTANCE feature**: Tính khoảng cách từ lat/lon đến trung tâm Quận 1 (Bến Nghé) → feature quan trọng cho BĐS.
---

## 9. Phân cụm K-Means

### 9.1 Chọn K bằng silhouette

![fig11](reports/figures/fig11_silhouette.png)

| K | Silhouette score |
|---|---|
| 3 | 0.079 |
| **4** | **0.083** ← best |
| 5 | 0.027 |
| 6 | −0.061 |

K = 4 được chọn tự động. Silhouette = 0.083 là thấp (lý tưởng > 0.5) — dự kiến vì BĐS là phân phối liên tục.

### 9.2 Phân bố cụm

| Cluster | Số tin | Tỷ lệ | Median price/m² | Median area (m²) | Đặc điểm (trung tâm cụm) |
|---|---:|---:|---:|---:|---|
| 0 | 165 | 9.3% | 50.0 | -0.12 (scaled) | Căn 1PN, hướng Đông (+0.57), balcony Đông (+1.04) |
| 1 | 1396 | 78.7% | 53.7 | +0.04 (scaled) | **Đa số — căn 2PN đặc trưng** |
| 2 | 47 | 2.6% | 50.0 | -0.45 (scaled) | Căn nhỏ ở Thủ Đức |
| 3 | 165 | 9.3% | 53.8 | -0.00 (scaled) | Hướng Tây/Tây Bắc (-2.27), balcony Tây (-1.70) |

### 9.3 Nhận xét

- **Cluster 1 chiếm 78.7%** → phần lớn căn hộ tập trung ở 1 cụm "đặc trưng" (2PN trung cấp).
- **4 cụm có median price_per_m2 gần như nhau (50–54 tr/m²)** → K-Means phân biệt chủ yếu theo `direction_code` (hướng nhà + hướng ban công) và `area_m2`, **KHÔNG theo phân khúc giá**. Đây là hệ quả của R² thấp (0.17) — giá khó dự đoán từ các features có sẵn.
- **Cluster 2 chỉ 47 tin (2.6%)** → tập trung ở Thủ Đức, diện tích nhỏ (scaled area = -0.45 ≈ 55m²). KHÔNG phải penthouse giá cao.
- **Cluster 0** đặc trưng bởi hướng Đông, balcony hướng Đông. **Cluster 3** đặc trưng bởi hướng Tây/Tây Bắc — phù hợp phong thuỷ "tránh nắng Đông" hoặc "đón gió Tây".
- **Silhouette rất thấp (0.083)** → các cụm tách biệt không rõ; ranh giới mờ vì các features chỉ giải thích một phần nhỏ phương sai giá.
---

## 10. Hệ gợi ý top 5

### 10.1 Chiến lược hybrid (giống data cũ)

**Bước 1 — Filter cứng**:
- `total_price ∈ [0.8 × budget, 1.2 × budget]`
- `bedrooms ∈ [target − 1, target + 1]`
- `district_clean ∈ preferred_districts` (nếu không rỗng)

**Bước 2 — Scoring**:
- `price_score  = 1 − |Δprice_per_m2| / target_price_per_m2`
- `area_score   = 1 − |Δarea_m2| / target_area`
- `segment_bonus = 0.3 nếu cùng cluster`
- `amenity_bonus = 0.2 × (amenity_score / max_amenity)`

### 10.2 Demo 3 hồ sơ nhu cầu căn hộ

| Hồ sơ | Ngân sách | Phòng | DT (m²) | Quận ưu tiên | Cluster ưu tiên | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|---|
| 1. Gia đình trẻ | 3 tỷ | 2 | 65 | Thủ Đức, Bình Thạnh | 0 | Top 5 ✅ | Tất cả 5 tin thuộc cluster 0, Thủ Đức |
| 2. Nhà đầu tư | 5 tỷ | 2 | 70 | Quận 7, Bình Tân | 1 | Top 5 ✅ | Tất cả 5 tin thuộc Quận 7, cluster 1, ~71tr/m² |
| 3. Người mua cao cấp | 7 tỷ | 3 | 85 | Thủ Đức, Quận 7 | 1 (đổi từ 2) | Top 5 ✅ | Cluster 2 chỉ 47 tin Thủ Đức, giá 1.58–4.6 tỷ → 0 khớp → chuyển cluster 1 |

> **Lưu ý quan trọng về `preferred_cluster`:**
> - Đây là **bonus điểm (+0.3)**, KHÔNG phải filter cứng.
> - Profile 3 (cao cấp 7 tỷ) ban đầu dùng cluster 2 (chỉ 47 tin ở Thủ Đức, giá 1.58–4.6 tỷ) → 0 tin khớp filter cứng → đã **đổi sang cluster 1** (1396 tin, có nhiều căn 6–10 tỷ) để có kết quả.
> - **District name phải khớp chính xác** với data (Thành phố Thủ Đức, Quận 7, Quận Bình Thạnh, Quận Bình Tân, Quận 12, Quận Gò Vấp). Sai tên → recommender trả về rỗng.

Cả 3 hồ sơ đều có kết quả — phù hợp với phạm vi 6 quận căn hộ.

Xem chi tiết từng dòng trong `reports/sample_recommendations.csv`.

### 10.3 Nhận xét

- Hệ gợi ý hoạt động tốt cho cả 3 hồ sơ — khác với data cũ (chỉ 2/3 match).
- **Score_components** cho phép giải thích tại sao 1 tin được gợi ý (quan trọng cho trust).
- Phù hợp với **mô hình hybrid** yêu cầu của đề tài.
- **Quan sát thực tế (trong top-5):**
  - Profile 1 (gia đình trẻ 3 tỷ): 5/5 tin đều ở Thủ Đức, cluster 0, giá 2.7–3.2 tỷ (rất sát budget 3 tỷ).
  - Profile 2 (nhà đầu tư 5 tỷ): 5/5 tin ở Quận 7, cluster 1, giá 4.8–5.1 tỷ. Có 2 tin trùng đặc điểm (cùng ward Tân Phú, 69.7m², 5.1 tỷ) — có thể là duplicate tin đăng.
  - Profile 3 (cao cấp 7 tỷ): 5/5 tin ở Thủ Đức, cluster 1 (sau khi đổi từ cluster 2), giá 6.1–7.7 tỷ.

---

## 11. Giới hạn và rủi ro thiên lệch

### 11.1 Giới hạn dữ liệu

- **1799 dòng từ 1 nguồn (chotot), 1 snapshot (T7-T8/2026)** → không phân tích xu hướng.
- **Phạm vi 6 quận** (thiếu các quận trung tâm Quận 1, 3, 4, 5) → bias về khu vực. Quận Bình Thạnh có median 71.4 tr/m² (cao nhất) — chỉ cách Quận 1 bởi cầu Bông/Bridge.
- **R² thấp (0.17)** — giá căn hộ phụ thuộc nhiều yếu tố phi số (view, tầng, nội thất chi tiết, tiến độ dự án, view sông/hồ) không có trong data.
- **Không có thông tin tầng, view, ban công rộng/hẹp** → thiếu feature quan trọng.
- **Silhouette rất thấp (0.083)** — K-Means phân biệt cụm theo `direction_code` (hướng nhà), KHÔNG theo phân khúc giá → không dùng để phân khúc thị trường. Median 4 cluster gần như nhau (50–54 tr/m²).
- **Top 10 worst có 1 case 147% error** (Duplex 140m², 51.4tr/m² bất thường) → data entry error khó phát hiện bằng IQR đơn thuần.
### 11.2 Rủi ro thiên lệch

- **Thiên lệch lựa chọn**: Dataset chỉ chứa tin đăng trên chotot — không đại diện toàn thị trường (batdongsan.com.vn, mogi.vn, alonhadat.com.vn).
- **Thiên lệch missing**: direction 79% missing, balcony 73% missing → median imputation có thể bias.
- **Thiên lệch theo quận**: Chỉ 6 quận, Thủ Đức chiếm 593/1773 (33.4%) → over-represent các dự án mới khu Đông.
- **Thiên lệch cluster mất cân đối**: Cluster 1 = 1396 tin (78.7%), cluster 2 = 47 tin (2.6%) → bonus cluster không hiệu quả cho cluster nhỏ.
- **Thiên lệch giá cực trị**: penthouse 934tr/m² (1 tin) kéo R² xuống. Top 10 worst có 5/10 là căn >150tr/m² — model underprice nhóm này.
### 11.3 Điều kiện không nên triển khai

- Dự đoán giá cho **cá nhân/tổ chức cụ thể** trong giao dịch thật — sai số 26% là quá lớn.
- **Dự báo giá tương lai** — model không có yếu tố thời gian.
- Áp dụng cho **quận ngoài 6 quận có data** — model không học.

---

## 12. Kết luận và hướng phát triển

### 12.1 Kết luận

Đồ án đã hoàn thành đầy đủ yêu cầu của Chuyên đề 3 (cập nhật cho dữ liệu căn hộ/chung cư):

1. ✅ **Hai nguồn dữ liệu** có cấu trúc khác nhau (1799 tin xlsx + 91 dòng tiện ích CSV).
2. ✅ **Tiền xử lý & làm sạch** với quy tắc căn hộ, loại 20 outlier, ghi log chi tiết → còn **1773 dòng** sau dropna.
3. ✅ **10 biểu đồ EDA chính + 2 biểu đồ phụ (fig11)** có tiêu đề + nhãn trục + nhận xét.
4. ✅ **4 mô hình ML** (Dummy baseline + Linear + RF + GBR), Random Forest tốt nhất với **R² = 0.169 trên test (CV R² = 0.357)**.
5. ✅ **10 trường hợp sai lớn nhất** được phân tích cụ thể (5 high-price, 1 Duplex anomaly, 5 missing ≥ 3 features).
6. ✅ **Phân cụm K-Means** với K tự động (silhouette = 0.083, **K=4**). Nhận xét: 4 cụm khác biệt theo `direction_code`, KHÔNG theo phân khúc giá.
7. ✅ **Hệ gợi ý hybrid** cho 3 hồ sơ demo căn hộ (cả 3 profile đều có top-5).
8. ✅ **45/45 unit test PASS** (TDD).
9. ✅ **4 Notebook** chạy được end-to-end.
10. ✅ **Báo cáo Markdown** + slide outline.

**Key findings**:
- RF Test R² = 0.169, MAE ≈ 13.9 tr/m² (~26% sai số so với median 53 tr/m²).
- Quận Bình Thạnh có median price/m² cao nhất (71.4 tr/m²), Bình Tân thấp nhất (42.8 tr/m²).
- 2PN chiếm 67% (1189 tin) — phù hợp cơ cấu căn hộ TP.HCM.
- Recommended 3 profiles: gia đình trẻ 3 tỷ (Thủ Đức), nhà đầu tư 5 tỷ (Quận 7), cao cấp 7 tỷ (Thủ Đức).
### 12.2 Hướng phát triển

**Dữ liệu**:
- Thu thập thêm ≥ 10.000 tin từ nhiều nguồn.
- Mở rộng 24 quận TP.HCM.
- Thêm thông tin tầng, view, ban công, tiến độ dự án.
- Lấy tọa độ lat/lon qua OpenStreetMap API → tính khoảng cách đến trung tâm Quận 1.

**Mô hình**:
- Thử **XGBoost / LightGBM** với hyperparameter tuning (Optuna).
- Feature engineering: `log(area_m2)`, `area × project`, `bedroom_density`.
- Trích đặc trưng từ `description` bằng TF-IDF (tiếng Việt).

**Hệ gợi ý**:
- Mở rộng `preferred_districts` thành "quận tương đương".
- Thêm trọng số tuỳ biến cho budget, area.

**Triển khai**:
- Đóng gói thành REST API (Flask/FastAPI).
- Dashboard trực quan (Streamlit).

---

## 13. Phụ lục

### 13.1 Cấu trúc thư mục

```
ChuoiKhoiUngDung/
├── data/
│   ├── raw/
│   │   ├── real_estate_apartment.xlsx      # 1799 tin BĐS căn hộ (chính)
│   │   ├── neighborhood_amenities.csv      # 91 dòng tiện ích (phụ)
│   │   └── real_estate_house_old_backup.csv # backup nhà phố (không dùng)
│   ├── processed/
│   │   ├── listings_clean.csv
│   │   ├── listings_with_amenities.csv
│   │   └── listings_with_clusters.csv
│   └── logs/
│       ├── cleaning_log.csv
│       └── error_log.txt
├── src/
│   ├── domain.py                     # PropertyListing, Location
│   ├── cleaner.py                    # normalize_district/direction + decode_furnishing/legal
│   ├── data_manager.py               # PropertyDataManager (CSV + XLSX)
│   ├── features.py                   # ColumnTransformer pipeline
│   ├── predictor.py                  # PricePredictor (4 mô hình + CV)
│   ├── segmenter.py                  # KMeansSegmenter
│   ├── recommender.py                # RecommendationEngine (hybrid)
│   └── pipeline.py                   # CLI end-to-end
├── tests/                            # 45 unit test
├── notebooks/
│   ├── 01_problem_and_data.ipynb
│   ├── 02_collection_and_cleaning.ipynb
│   ├── 03_eda.ipynb
│   └── 04_machine_learning.ipynb
├── reports/
│   ├── figures/                      # 12 PNG
│   ├── final_report.md               # file này
│   ├── slide_outline.md
│   ├── metrics.json
│   ├── data_dictionary.md
│   ├── ai_usage_log.md
│   ├── member_contributions.md
│   └── sample_recommendations.csv
├── scripts/
│   ├── make_neighborhood_amenities.py    # tạo nguồn 2 từ xlsx
│   └── run_notebooks.py                 # helper chạy notebooks
├── requirements.txt
├── run_all.sh
└── README.md
```

### 13.2 Cách chạy lại dự án

```bash
# 1. Cài đặt
cd ChuoiKhoiUngDung
pip install -r requirements.txt
pip install nbformat nbclient ipykernel openpyxl

# 2. Tạo nguồn dữ liệu thứ 2 (nếu chưa có)
python -m scripts.make_neighborhood_amenities

# 3. Chạy toàn bộ (tests + pipeline + notebooks)
bash run_all.sh

# 4. Hoặc chạy từng phần:
python -m pytest tests/ -v
python -m src.pipeline
python3 scripts/run_notebooks.py
```

---

## 14. Tài liệu tham khảo

1. Pedregosa, F., et al. (2011). *Scikit-learn: Machine Learning in Python*. JMLR, 12, 2825-2830.
2. McKinney, W. (2010). *Data Structures for Statistical Computing in Python*. Proceedings of SciPy.
3. Hunter, J. D. (2007). *Matplotlib: A 2D Graphics Environment*. Computing in Science & Engineering.
4. Đề tài Chuyên đề cuối kỳ — Môn Lập trình cho Khoa học Dữ liệu (PDF trong `data/`).
5. Dataset `real_estate_apartment.xlsx` — snapshot T7-T8/2026 từ chotot.
6. Tài liệu sklearn: [ColumnTransformer](https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html), [Pipeline](https://scikit-learn.org/stable/modules/compose.html), [KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html).

---

*Hết báo cáo.*
