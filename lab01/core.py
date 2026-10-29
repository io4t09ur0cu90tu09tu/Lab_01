"""Чисте функціональне ядро для розрахунку мобільного тарифу (Варіант 11).

Ключові слова: mobile, tariff, minutes, sms, traffic, data, bonus, monthly, cost.
Не містить побічних ефектів (I/O) та не мутує вхідні дані.
"""

from typing import Callable, Iterable, List, TypedDict, TypeVar

# --- Анотації типів предметної області ---


class TariffPlan(TypedDict):
    base_fee: float
    free_minutes: int
    free_sms: int
    free_gb: float
    price_per_min: float
    price_per_sms: float
    price_per_gb: float


class UsageRecord(TypedDict):
    user_id: int
    minutes_used: int
    sms_used: int
    gb_used: float
    plan: TariffPlan


class ProcessedUsageRecord(UsageRecord):
    extra_minutes_cost: float
    extra_sms_cost: float
    extra_gb_cost: float
    monthly_cost: float


# Синоніми типів для політик Callable
PricingFn = Callable[[UsageRecord], float]
BonusFn = Callable[[float], float]
FilterFn = Callable[[UsageRecord], bool]

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# --- Чисті функції предметної області ---


def calculate_extra_minutes_cost(record: UsageRecord) -> float:
    """Обчислює вартість понаднормових хвилин (minutes)."""
    plan = record["plan"]
    extra_min = max(0, record["minutes_used"] - plan["free_minutes"])
    return extra_min * plan["price_per_min"]


def calculate_extra_sms_cost(record: UsageRecord) -> float:
    """Обчислює вартість понаднормових SMS."""
    plan = record["plan"]
    extra_sms = max(0, record["sms_used"] - plan["free_sms"])
    return extra_sms * plan["price_per_sms"]


def calculate_extra_gb_cost(record: UsageRecord) -> float:
    """Обчислює вартість понаднормового інтернет-трафіку/даних (traffic, data, gb)."""
    plan = record["plan"]
    extra_gb = max(0.0, record["gb_used"] - plan["free_gb"])
    return extra_gb * plan["price_per_gb"]


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    """Компоновка двох функцій: (f ∘ g)(x) = f(g(x))."""
    return lambda x: f(g(x))


def make_loyalty_bonus_policy(discount_percent: float) -> BonusFn:
    """Фабрика функцій: повертає політику нарахування бонусів/знижок (bonus, tariff)."""

    def apply_bonus(cost: float) -> float:
        return cost * (1.0 - discount_percent)

    return apply_bonus


def with_monthly_cost(
    record: UsageRecord,
    extra_min: float,
    extra_sms: float,
    extra_gb: float,
    final_cost: float,
) -> ProcessedUsageRecord:
    """Повертає новий словник з розрахованими витратами (monthly, cost), не мутуючи оригінал."""
    return {
        **record,
        "extra_minutes_cost": round(extra_min, 2),
        "extra_sms_cost": round(extra_sms, 2),
        "extra_gb_cost": round(extra_gb, 2),
        "monthly_cost": round(final_cost, 2),
    }


def make_tariff_processor(
    *,
    accept: FilterFn,
    bonus_policy: BonusFn,
) -> Callable[[Iterable[UsageRecord]], dict[str, object]]:
    """Параметризована фабрика обробника тарифів (фільтрація та розрахунок)."""

    def process(records: Iterable[UsageRecord]) -> dict[str, object]:
        processed_list: List[ProcessedUsageRecord] = []
        total_revenue = 0.0

        for rec in records:
            if not accept(rec):
                continue

            extra_min = calculate_extra_minutes_cost(rec)
            extra_sms = calculate_extra_sms_cost(rec)
            extra_gb = calculate_extra_gb_cost(rec)

            subtotal = rec["plan"]["base_fee"] + extra_min + extra_sms + extra_gb
            final_cost = bonus_policy(subtotal)

            new_rec = with_monthly_cost(rec, extra_min, extra_sms, extra_gb, final_cost)
            processed_list.append(new_rec)
            total_revenue += final_cost

        return {
            "count": len(processed_list),
            "revenue": round(total_revenue, 2),
            "records": processed_list,
        }

    return process