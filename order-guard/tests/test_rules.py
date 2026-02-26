"""Tests for order evaluation rules."""
from order_guard.rules import evaluate_order, RuleResult


class TestProductionCostRule:
    def test_under_limit_passes(self):
        result = evaluate_order(
            production_cost=25.00,
            items=[{"quantity": 1}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is True
        assert result.violated_rule is None

    def test_at_limit_passes(self):
        result = evaluate_order(
            production_cost=50.00,
            items=[{"quantity": 1}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is True

    def test_over_limit_fails(self):
        result = evaluate_order(
            production_cost=75.00,
            items=[{"quantity": 1}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is False
        assert result.violated_rule == "max_cost"
        assert "75.00" in result.reason


class TestItemQuantityRule:
    def test_within_limit_passes(self):
        result = evaluate_order(
            production_cost=10.00,
            items=[{"quantity": 2}, {"quantity": 3}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is True

    def test_over_limit_fails(self):
        result = evaluate_order(
            production_cost=10.00,
            items=[{"quantity": 5}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is False
        assert result.violated_rule == "max_item_qty"

    def test_multiple_items_one_over_fails(self):
        result = evaluate_order(
            production_cost=10.00,
            items=[{"quantity": 1}, {"quantity": 4}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is False
        assert result.violated_rule == "max_item_qty"


class TestVelocityRule:
    def test_under_velocity_passes(self):
        result = evaluate_order(
            production_cost=10.00,
            items=[{"quantity": 1}],
            recent_order_count=3,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is True

    def test_at_velocity_limit_fails(self):
        result = evaluate_order(
            production_cost=10.00,
            items=[{"quantity": 1}],
            recent_order_count=5,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is False
        assert result.violated_rule == "velocity"


class TestRulePriority:
    """First failing rule is reported."""

    def test_cost_checked_before_quantity(self):
        result = evaluate_order(
            production_cost=100.00,
            items=[{"quantity": 10}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.violated_rule == "max_cost"
