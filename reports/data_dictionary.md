# Từ điển dữ liệu — Đồ án KHDL Chuyên đề 3

## Nguồn 1: `data/raw/real_estate_apartment.xlsx` (1799 dòng)

| Cột | Kiểu | Mô tả | Missing % | Ghi chú xử lý |
|---|---|---|---|---|
| `listing_id` | int | Mã tin đăng (unique) | 0.00% | Khóa chính, không dùng làm feature |
| `title` | str | Tiêu đề tin (có emoji) | 0.00% | Không dùng làm feature (chưa trích đặc trưng văn bản) |
| `description` | str | Mô tả dài | 0.00% | Không dùng làm feature |
| `property_type` | str | Loại hình | 0.00% | Chỉ có 1 giá trị "Căn hộ/Chung cư" → không dùng |
| `province` | str | Tỉnh/TP | 0.00% | Chỉ có "Tp Hồ Chí Minh" → không dùng |
| `district` | str | Quận (6 giá trị) | 0.00% | Pass-through, tạo `district_clean` |
| `ward` | str | Phường/xã (83 giá trị) | 0.89% | Dùng làm khóa join với `neighborhood_amenities.csv` |
| `street` | str | Tên đường (422 giá trị) | 0.56% | Không dùng làm feature |
| `latitude`, `longitude` | float | Toạ độ thực | 0.94% | Không dùng làm feature (ML tabular) |
| `project_name` | str | Tên dự án (288 giá trị) | 20.9% | Dùng làm categorical feature (sau khi impute) |
| `area_m2` | float | Diện tích (m²) | 0.33% | Lọc outlier < 10 hoặc > 500; feature chính |
| `bedrooms` | float | Số phòng ngủ | 0.17% | Lọc outlier > 10; Impute median; feature chính |
| `bathrooms` | float | Số phòng tắm | 15.6% | Impute median; feature phụ |
| `direction` | float | Mã hướng 1..8 | 78.9% | Decode → `direction_clean`; mã giữ làm feature số |
| `balcony_direction` | float | Mã hướng ban công 1..8 | 73.2% | Giữ mã làm feature số |
| `furnishing_status` | float | Mã nội thất 1..4 | 34.4% | Decode → `furnishing_label`; mã giữ làm feature số |
| `legal_status` | float | Mã pháp lý 1,2,4,5,6 | 20.0% | Decode → `legal_label`; mã giữ làm feature số |
| `apartment_type` | int | Mã loại căn hộ 1..6 | 0.00% | Feature số |
| `total_price` | int | Tổng giá (VND) | 0.00% | Lọc outlier < 100 triệu; dùng trong recommender |
| `price_text` | str | Giá dạng text ("3,19 tỷ") | 0.00% | Không dùng làm feature |
| `price_per_m2` | float | Giá/m² tính sẵn | 0.33% | **Tính lại** từ `total_price / area_m2`; là **target** |
| `image_count` | int | Số ảnh đăng kèm | 0.00% | Feature số (proxy cho chất lượng tin) |
| `posted_at` | datetime | Ngày đăng | 0.00% | Chỉ dùng cho EDA (xem theo tháng) |
| `source`, `status`, `url` | str | Metadata nguồn | 0.00% | Không dùng |

**Cột được tạo thêm bởi pipeline:**

| Cột | Nguồn gốc | Mô tả |
|---|---|---|
| `district_clean` | `district` qua `normalize_district()` | Pass-through + strip (đã chuẩn trong xlsx) |
| `direction_clean` | `direction` qua `normalize_direction()` | 8 hướng chuẩn: Đông, Tây, Nam, Bắc, Đông Nam, Tây Nam, Đông Bắc, Tây Bắc |
| `furnishing_label` | `furnishing_status` qua `decode_furnishing()` | Không nội thất / Nội thất cơ bản / Nội thất đầy đủ / Nội thất cao cấp |
| `legal_label` | `legal_status` qua `decode_legal()` | Đang cập nhật / Sổ hồng lâu dài / HĐMB / Sổ hồng chung / Sổ hồng riêng |
| `direction_code` / `balcony_code` / `furnishing_code` / `legal_code` | copy cột gốc | Mã số dùng làm feature ML |
| `price_per_m2` | `total_price / area_m2` | Giá/m² đã tính lại |
| `amenity_score` | merge với `neighborhood_amenities.csv` | Điểm tiện ích tổng hợp (NaN nếu không match) |
| `cluster` | K-Means | Nhãn cụm (0..K-1) |
| `score_total`, `score_components` | RecommendationEngine | Điểm gợi ý và các thành phần |

## Nguồn 2: `data/raw/neighborhood_amenities.csv` (89 dòng)

| Cột | Kiểu | Mô tả | Phạm vi giá trị |
|---|---|---|---|
| `ward` | str | Phường/xã | từ data xlsx |
| `district_clean` | str | Quận | 6 giá trị (matching với data chính) |
| `school_count` | int | Số trường học | 1–12 |
| `hospital_count` | int | Số bệnh viện | 0–6 |
| `supermarket_count` | int | Số siêu thị | 0–10 |
| `park_count` | int | Số công viên | 0–8 |
| `bus_stops_count` | int | Số trạm bus | 1–20 |
| `amenity_score` | float | Điểm tiện ích tổng h�p | Công thức: `1 + 0.3*school + 0.5*hospital + 0.2*super + 0.4*park + 0.1*bus` |

**Ghi chú:** Đây là nguồn dữ liệu tự tạo (deterministic, seed=42), sinh từ cặp (district, ward) có trong data xlsx — mô phỏng thông tin tiện ích theo khu vực. Đáp ứng yêu cầu "ít nhất 2 nguồn / 2 loại tập tin có cấu trúc khác nhau" của đồ án.

## Quyết định feature cho mô hình

```python
NUMERIC_COLS = [
    "area_m2", "bedrooms", "bathrooms",
    "direction_code", "balcony_code", "furnishing_code",
    "legal_code", "image_count", "apartment_type",
]
CATEGORICAL_COLS = ["district_clean", "direction_clean", "project_name"]
TARGET = "price_per_m2"
```

Pipeline sklearn `ColumnTransformer`:
- Numeric: `SimpleImputer(median)` → `StandardScaler`
- Categorical: `SimpleImputer(constant="missing")` → `OneHotEncoder(handle_unknown="ignore", min_frequency=10)`
