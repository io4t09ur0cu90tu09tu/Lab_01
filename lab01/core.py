"""Чисте функціональне ядро для розрахунку мобільного тарифу (Варіант 11).

Ключові слова: mobile, tariff, minutes, sms, traffic, data, bonus, monthly, cost, limit, filter.
Не містить побічних ефектів (I/O) та не мутує вхідні дані[cite: 9].
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
    extra_traffic_cost: float
    monthly_cost: float


# Синоніми типів для політик Callable
BonusFn = Callable[[float], float]
FilterFn = Callable[[UsageRecord], bool]

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# --- Чисті функції предметної області згідно з вимогами ---


def calculate_minutes_cost(record: UsageRecord) -> float:
    """Обчислює вартість понаднормових хвилин (minutes) понад ліміт (limit)."""
    plan = record["plan"]
    extra_min = max(0, record["minutes_used"] - plan["free_minutes"])
    return extra_min * plan["price_per_min"]


def calculate_sms_cost(record: UsageRecord) -> float:
    """Обчислює вартість понаднормових SMS-повідомлень (sms) понад ліміт."""
    plan = record["plan"]
    extra_sms = max(0, record["sms_used"] - plan["free_sms"])
    return extra_sms * plan["price_per_sms"]


def calculate_traffic_cost(record: UsageRecord) -> float:
    """Обчислює вартість понаднормового інтернет-трафіку/даних (traffic, data) понад ліміт."""
    plan = record["plan"]
    extra_gb = max(0.0, record["gb_used"] - plan["free_gb"])
    return extra_gb * plan["price_per_gb"]


def calculate_monthly_cost(base_fee: float, minutes_cost: float, sms_cost: float, traffic_cost: float, bonus_policy: BonusFn) -> float:
    """Обчислює фінальну місячну (monthly) вартість (cost) з урахуванням базової плати та бонусів (bonus)."""
    subtotal = base_fee + minutes_cost + sms_cost + traffic_cost
    return bonus_policy(subtotal)


def with_monthly_cost(
    record: UsageRecord,
    extra_min_cost: float,
    extra_sms_cost: float,
    extra_traffic_cost: float,
    final_monthly_cost: float,
) -> ProcessedUsageRecord:
    """Повертає новий словник з розрахованими витратами (monthly, cost), не мутуючи оригінал[cite: 9]."""
    return {
        **record,
        "extra_minutes_cost": round(extra_min_cost, 2),
        "extra_sms_cost": round(extra_sms_cost, 2),
        "extra_traffic_cost": round(extra_traffic_cost, 2),
        "monthly_cost": round(final_monthly_cost, 2),
    }


def filter_tariffs(records: Iterable[UsageRecord], accept: FilterFn) -> Iterable[UsageRecord]:
    """Фільтрує записи тарифів (tariff, filter, limit) за заданим критерієм."""
    return (rec for rec in records if accept(rec))


def make_processor(
    *,
    filter_fn: FilterFn,
    bonus_policy: BonusFn,
) -> Callable[[Iterable[UsageRecord]], dict[str, object]]:
    """Параметризована фабрика обробника мобільних тарифів (mobile, tariff) через Callable[cite: 9]."""

    def process(records: Iterable[UsageRecord]) -> dict[str, object]:
        valid_records = filter_tariffs(records, filter_fn)
        processed_list: List[ProcessedUsageRecord] = []
        total_revenue = 0.0

        for rec in valid_records:
            min_cost = calculate_minutes_cost(rec)
            sms_cost = calculate_sms_cost(rec)
            traf_cost = calculate_traffic_cost(rec)
            
            monthly_cost_val = calculate_monthly_cost(
                rec["plan"]["base_fee"],
                min_cost,
                sms_cost,
                traf_cost,
                bonus_policy
            )

            new_rec = with_monthly_cost(rec, min_cost, sms_cost, traf_cost, monthly_cost_val)
            processed_list.append(new_rec)
            total_revenue += monthly_cost_val

        return {
            "count": len(processed_list),
            "revenue": round(total_revenue, 2),
            "records": processed_list,
        }

    return process