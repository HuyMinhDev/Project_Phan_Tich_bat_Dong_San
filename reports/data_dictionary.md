# Từ điển dữ liệu — Đồ án KHDL Chuyên đề 3

## Nguồn 1: `data/raw/real_estate_with_price_per_m2.csv` (3000 dòng)

| Cột | Kiểu | Mô tả | Missing % | Ghi chú xử lý |
|---|---|---|---|---|
| `listing_id` | int | Mã tin đăng | 0.00% | Khóa chính, không dùng làm feature |
| `title` | str | Tiêu đề tin | 0.00% | Dùng để trích `street_name`, `project_name` (regex) |
| `description` | str | Mô tả dài | 0.00% | Không dùng làm feature (chưa trích đặc trưng văn bản) |
| `property_type` | str | Loại hình | 0.00% | Chỉ có 1 giá trị "Nhà" → không dùng |
| `province` | str | Tỉnh/TP | 0.00% | Chỉ có "Hồ Chí Minh" → không dùng |
| `district` | str | Quận/huyện (thô) | 0.53% | Chuẩn hóa → `district_clean` |
| `ward` | str | Phường/xã | 6.67% | Dùng làm khóa join với `neighborhood_amenities.csv` |
| `street_name` | str | Tên đường | 26.50% | Không dùng làm feature (missing cao) |
| `project_name` | str | Tên dự án | 98.60% | BỎ (missing > 98%) |
| `total_price` | float | Tổng giá (VND) | 0.87% | Lọc outlier < 100 triệu; dùng làm target phụ |
| `area_m2` | float | Diện tích (m²) | 0.00% | Lọc outlier < 5 hoặc > 1000; feature chính |
| `price_per_m2` | float | Giá/m² tính sẵn | 0.87% | **Tính lại** từ `total_price / area_m2` để đảm bảo nhất quán; là **target** của mô hình |
| `floor_count` | float | Số tầng | 74.53% | Impute median khi fit |
| `frontage_width` | float | Mặt tiền (m) | 8.13% | Impute median khi fit |
| `house_depth` | float | Chiều sâu nhà (m) | 99.57% | BỎ (missing > 99%) |
| `road_width` | float | Độ rộng đường (m) | 84.67% | BỎ (missing > 84%) |
| `bedrooms` | float | Số phòng ngủ | 16.97% | Lọc outlier > 15; Impute median; feature chính |
| `bathrooms` | float | Số phòng tắm | 19.07% | Impute median; feature phụ |
| `house_direction` | str | Hướng nhà | 0.00% | Chuẩn hóa về 8 hướng → `direction_clean` |
| `posted_at` | str | Ngày đăng (ISO) | 0.00% | Chỉ dùng cho EDA (xem theo tháng), không feature |

**Cột được tạo thêm:**

| Cột | Nguồn gốc | Mô tả |
|---|---|---|
| `district_clean` | `district` qua `normalize_district()` | "Quận 1".."Quận 12" / "Quận Bình Thạnh" / "Huyện Củ Chi" |
| `direction_clean` | `house_direction` qua `normalize_direction()` | 8 hướng chuẩn: Đông, Tây, Nam, Bắc, Đông Nam, Tây Nam, Đông Bắc, Tây Bắc |
| `price_per_m2` | `total_price / area_m2` | Giá/m² đã tính lại |
| `amenity_score` | merge với `neighborhood_amenities.csv` | Điểm tiện ích tổng hợp (NaN nếu không match) |
| `cluster` | K-Means | Nhãn cụm (0, 1, 2) |
| `score_total`, `score_components` | RecommendationEngine | Điểm gợi ý và các thành phần |

## Nguồn 2: `data/raw/neighborhood_amenities.csv` (100 dòng)

| Cột | Kiểu | Mô tả | Phạm vi giá trị |
|---|---|---|---|
| `ward` | str | Phường/xã | ~100 giá trị (từ dataset chính) |
| `district_clean` | str | Quận/huyện (đã chuẩn) | 22 giá trị |
| `school_count` | int | Số trường học | 1–12 |
| `hospital_count` | int | Số bệnh viện | 0–6 |
| `supermarket_count` | int | Số siêu thị | 0–10 |
| `park_count` | int | Số công viên | 0–8 |
| `bus_stops_count` | int | Số trạm bus | 1–20 |
| `amenity_score` | float | Điểm tiện ích tổng hợp | Công thức: `1 + 0.3*school + 0.5*hospital + 0.2*super + 0.4*park + 0.1*bus` |

**Ghi chú:** Đây là nguồn dữ liệu tự tạo (deterministic, seed=42), mô phỏng thông tin tiện ích theo khu vực — đáp ứng yêu cầu "ít nhất 2 nguồn / 2 loại tập tin có cấu trúc khác nhau" của đồ án.

## Quyết định feature cho mô hình

```python
NUMERIC_COLS = ["area_m2", "bedrooms", "bathrooms", "floor_count", "frontage_width"]
CATEGORICAL_COLS = ["district_clean", "direction_clean"]
TARGET = "price_per_m2"
```

Pipeline sklearn `ColumnTransformer`:
- Numeric: `SimpleImputer(median)` → `StandardScaler`
- Categorical: `SimpleImputer(constant="missing")` → `OneHotEncoder(handle_unknown="ignore", min_frequency=10)`