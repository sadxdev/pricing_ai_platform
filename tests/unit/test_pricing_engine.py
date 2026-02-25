import pytest
from app.services.pricing_engine import PricingEngine


def test_calculate_price_returns_expected_keys():
    result = PricingEngine.calculate_price(
        cost_price=100.0,
        base_price=150.0,
        predicted_demand=50,
        avg_comp_price=160.0,
        min_comp_price=140.0,
        max_comp_price=180.0,
    )
    assert "recommended_price" in result
    assert "strategy" in result
    assert "min_allowed_price" in result
    assert "optimized_price" in result
    assert "expected_profit" in result


def test_price_is_above_cost():
    result = PricingEngine.calculate_price(
        cost_price=100.0,
        base_price=150.0,
        predicted_demand=50,
        avg_comp_price=160.0,
        min_comp_price=140.0,
        max_comp_price=180.0,
    )
    assert result["recommended_price"] >= 100.0


def test_price_floor_is_above_cost():
    result = PricingEngine.calculate_price(
        cost_price=100.0,
        base_price=150.0,
        predicted_demand=50,
        avg_comp_price=160.0,
        min_comp_price=140.0,
        max_comp_price=180.0,
    )
    assert result["min_allowed_price"] >= 100.0