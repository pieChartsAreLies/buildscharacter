"""Order evaluation rules. Pure functions, no I/O."""
from dataclasses import dataclass


@dataclass
class RuleResult:
    passed: bool
    violated_rule: str | None = None
    reason: str | None = None


def evaluate_order(
    production_cost: float,
    items: list[dict],
    recent_order_count: int,
    max_production_cost: float,
    max_item_qty: int,
    max_hourly_velocity: int,
) -> RuleResult:
    """Evaluate an order against all rules. Returns first violation or pass."""
    # Rule 1: production cost cap
    if production_cost > max_production_cost:
        return RuleResult(
            passed=False,
            violated_rule="max_cost",
            reason=f"Production cost ${production_cost:.2f} exceeds limit ${max_production_cost:.2f}",
        )

    # Rule 2: per-item quantity cap
    for item in items:
        if item.get("quantity", 0) > max_item_qty:
            return RuleResult(
                passed=False,
                violated_rule="max_item_qty",
                reason=f"Item quantity {item['quantity']} exceeds limit {max_item_qty}",
            )

    # Rule 3: hourly velocity cap
    if recent_order_count >= max_hourly_velocity:
        return RuleResult(
            passed=False,
            violated_rule="velocity",
            reason=f"Hourly order count {recent_order_count} exceeds limit {max_hourly_velocity}",
        )

    return RuleResult(passed=True)
