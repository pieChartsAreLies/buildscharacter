"""Tests for notification message formatting."""
from order_guard.notify import format_confirmed_message, format_held_message, format_error_message


class TestFormatConfirmedMessage:
    def test_basic_confirmed(self):
        msg = format_confirmed_message(
            order_id=12345,
            production_cost=18.50,
            retail_total=34.99,
            items=[{"name": "Build Character Sticker", "quantity": 2}],
        )
        assert "12345" in msg
        assert "18.50" in msg
        assert "34.99" in msg
        assert "Sticker" in msg
        assert "Confirmed" in msg


class TestFormatHeldMessage:
    def test_cost_violation(self):
        msg = format_held_message(
            order_id=12345,
            production_cost=75.00,
            retail_total=120.00,
            items=[{"name": "Hoodie", "quantity": 1}],
            rule_violated="max_cost",
            reason="Production cost $75.00 exceeds limit $50.00",
        )
        assert "12345" in msg
        assert "HELD" in msg or "Held" in msg
        assert "75.00" in msg
        assert "max_cost" in msg


class TestFormatErrorMessage:
    def test_error_message(self):
        msg = format_error_message(
            order_id=12345,
            error="Connection refused",
        )
        assert "12345" in msg
        assert "Error" in msg or "ERROR" in msg
        assert "Connection refused" in msg
