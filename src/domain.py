"""Domain dataclasses: PropertyListing, Location.

Đại diện cho một tin đăng căn hộ/chung cư (`PropertyListing`) và một vị trí
địa lý (`Location`). Cả hai đều là value-object bất biến, không có logic
nghiệp vụ phức tạp — logic nằm ở các module khác (cleaner, predictor,
recommender).

Schema phù hợp với `real_estate_apartment.xlsx`:
- `listing_id`     — PK
- `district_clean` — quận chuẩn (e.g. "Quận Bình Thạnh")
- `ward`           — phường/xã (giữ gốc để EDA xem chi tiết)
- `area_m2`        — diện tích (m²)
- `bedrooms`       — số phòng ngủ
- `bathrooms`      — số phòng tắm
- `total_price`    — giá (VND)
- `price_per_m2`   — giá/m² (VND/m²)
- `direction_code` — mã hướng chính (1..8)
- `direction_clean` — tên hướng đã decode (Đông/Tây/...)
- `balcony_code`   — mã hướng ban công (1..8)
- `furnishing_code` — mã tình trạng nội thất (1..4)
- `legal_code`     — mã tình trạng pháp lý (1,2,4,5,6)
- `latitude`, `longitude` — toạ độ (NaN nếu thiếu)
- `project_name`   — tên dự án
- `apartment_type` — mã loại căn hộ (1..6)
- `property_type`  — loại B�S (mặc định "Căn hộ/Chung cư")

Quy ước `price_band` (đơn vị VND/m²):
- `thap`         : < 50 triệu
- `trung_cap`    : 50 – 90 triệu
- `trung_cao`    : 90 – 150 triệu
- `cao`          : ≥ 150 triệu
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class PropertyListing:
    listing_id: int
    district_clean: str
    area_m2: float
    bedrooms: Optional[float]
    total_price: float
    price_per_m2: float
    ward: Optional[str] = None
    bathrooms: Optional[float] = None
    direction_code: Optional[float] = None
    direction_clean: Optional[str] = None
    balcony_code: Optional[float] = None
    furnishing_code: Optional[float] = None
    legal_code: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    project_name: Optional[str] = None
    apartment_type: Optional[float] = None
    property_type: Optional[str] = None
    price_band: str = field(default="trung_cap", init=False)

    def __post_init__(self) -> None:
        if self.area_m2 is None or self.area_m2 <= 0:
            raise ValueError(f"area_m2 phải > 0, nhận {self.area_m2}")
        if self.price_per_m2 is None or self.price_per_m2 <= 0:
            raise ValueError(f"price_per_m2 phải > 0, nhận {self.price_per_m2}")
        self.price_band = self._compute_price_band(self.price_per_m2)

    @staticmethod
    def _compute_price_band(price_per_m2: float) -> str:
        v = price_per_m2
        if v < 50_000_000:
            return "thap"
        if v < 90_000_000:
            return "trung_cap"
        if v < 150_000_000:
            return "trung_cao"
        return "cao"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Location:
    district_clean: str
    ward: str
    amenity_score: Optional[float] = None

    @property
    def label(self) -> str:
        return f"{self.district_clean}/{self.ward}"
