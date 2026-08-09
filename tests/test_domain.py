"""Test cho `src.domain` (PropertyListing, Location)."""

from __future__ import annotations

import pytest


def test_property_listing_basic():
    from src.domain import PropertyListing

    p = PropertyListing(
        listing_id=1,
        district_clean="Quận Bình Thạnh",
        area_m2=56.0,
        bedrooms=2,
        total_price=3_190_000_000,
        price_per_m2=57_000_000,
    )
    assert p.price_per_m2 == 57_000_000
    # 57tr/m² nằm trong [50tr, 90tr) → trung_cap
    assert p.price_band == "trung_cap"
    assert p.to_dict()["listing_id"] == 1
    assert p.to_dict()["district_clean"] == "Quận Bình Thạnh"


def test_property_listing_price_band_thap():
    from src.domain import PropertyListing

    p = PropertyListing(
        listing_id=2,
        district_clean="Huyện Bình Chánh",
        area_m2=70.0,
        bedrooms=2,
        total_price=2_500_000_000,
        price_per_m2=35_000_000,
    )
    assert p.price_band == "thap"


def test_property_listing_price_band_trung_cao():
    from src.domain import PropertyListing

    p = PropertyListing(
        listing_id=3,
        district_clean="Thành phố Thủ Đức",
        area_m2=80.0,
        bedrooms=3,
        total_price=10_000_000_000,
        price_per_m2=125_000_000,
    )
    assert p.price_band == "trung_cao"


def test_property_listing_price_band_cao():
    from src.domain import PropertyListing

    p = PropertyListing(
        listing_id=4,
        district_clean="Quận 1",
        area_m2=80.0,
        bedrooms=4,
        total_price=30_000_000_000,
        price_per_m2=375_000_000,
    )
    assert p.price_band == "cao"


def test_property_listing_rejects_invalid_area():
    from src.domain import PropertyListing

    with pytest.raises(ValueError):
        PropertyListing(
            listing_id=5,
            district_clean="Quận 3",
            area_m2=0,
            bedrooms=3,
            total_price=8e9,
            price_per_m2=100e6,
        )


def test_property_listing_rejects_invalid_price_per_m2():
    from src.domain import PropertyListing

    with pytest.raises(ValueError):
        PropertyListing(
            listing_id=6,
            district_clean="Quận 3",
            area_m2=80.0,
            bedrooms=3,
            total_price=8e9,
            price_per_m2=0,
        )


def test_property_listing_accepts_apartment_codes():
    """Căn hộ có các mã categorical số (direction, balcony, furnishing, legal)."""
    from src.domain import PropertyListing

    p = PropertyListing(
        listing_id=7,
        district_clean="Quận 7",
        area_m2=70.0,
        bedrooms=2,
        total_price=4_000_000_000,
        price_per_m2=57_000_000,
        direction_code=5.0,
        direction_clean="Đông Nam",
        balcony_code=3.0,
        furnishing_code=3.0,
        legal_code=6.0,
        latitude=10.7,
        longitude=106.7,
        project_name="Vinhomes Grand Park",
        apartment_type=1.0,
    )
    assert p.direction_clean == "\u0110ông Nam"
    assert p.furnishing_code == 3.0
    assert p.legal_code == 6.0
    assert p.project_name == "Vinhomes Grand Park"


def test_location_label():
    from src.domain import Location

    loc = Location(district_clean="Quận 7", ward="Tân Mỹ", amenity_score=4.5)
    assert loc.amenity_score == 4.5
    assert loc.label == "Quận 7/Tân Mỹ"


def test_location_amenity_optional():
    from src.domain import Location

    loc = Location(district_clean="Quận 7", ward="Tân Mỹ")
    assert loc.amenity_score is None
    assert loc.label == "Quận 7/Tân Mỹ"
