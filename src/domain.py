"""Domain dataclasses: PropertyListing, Location.

Đại diện cho một tin đăng bất động sản (`PropertyListing`) và một vị trí địa lý
(`Location`). Cả hai đều là value-object bất biến, không có logic nghiệp vụ
phức tạp — logic nằm ở các module khác (cleaner, predictor, recommender).

Quy ước `price_band` (đơn vị VND/m²):
- `thap`         : < 50 triệu
- `trung_cap`    : 50 – 120 triệu
- `trung_cao`    : 120 – 250 triệu
- `cao`          : ≥ 250 triệu
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
    floor_count: Optional[float] = None
    frontage_width: Optional[float] = None
    house_direction: Optional[str] = None
    property_type: Optional[str] = None
    price_band: str = field(default="trung_cap", init=False)

    def __post_init__(self) -> None:
        if self.area_m2 <= 0:
            raise ValueError(f"area_m2 phải > 0, nhận {self.area_m2}")
        if self.price_per_m2 <= 0:
            raise ValueError(f"price_per_m2 phải > 0, nhận {self.price_per_m2}")
        self.price_band = self._compute_price_band(self.price_per_m2)

    @staticmethod
    def _compute_price_band(price_per_m2: float) -> str:
        v = price_per_m2
        if v < 50_000_000:
            return "thap"
        if v < 120_000_000:
            return "trung_cap"
        if v < 250_000_000:
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