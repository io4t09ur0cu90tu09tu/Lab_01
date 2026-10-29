"""Оболонка для роботи з I/O та виклику чистого ядра."""

from typing import List
from core import UsageRecord, make_tariff_processor, make_loyalty_bonus_policy


def render_report(result: dict[str, object]) -> None:
    """Функція для відображення результатів (I/O)."""
    print("=== ЗВІТ РОЗРАХУНКУ МОБІЛЬНИХ ТАРИФІВ ===")
    print(f"Опрацьовано записів: {result['count']}")
    print("-" * 40)

    records = result.get("records", [])
    if isinstance(records, list):
        for rec in records:
            print(
                f"Користувач ID: {rec['user_id']} | "
                f"Абонплата: {rec['plan']['base_fee']} грн | "
                f"Понад ліміт: {rec['extra_minutes_cost'] + rec['extra_sms_cost'] + rec['extra_gb_cost']:.2f} грн | "
                f"Разом до сплати (monthly_cost): {rec['monthly_cost']} грн"
            )

    print("-" * 40)
    print(f"Загальний дохід (Revenue): {result['revenue']} грн\n")


def run() -> None:
    # Початкові дані
    sample_records: List[UsageRecord] = [
        {
            "user_id": 101,
            "minutes_used": 350,
            "sms_used": 40,
            "gb_used": 12.5,
            "plan": {
                "base_fee": 150.0,
                "free_minutes": 300,
                "free_sms": 50,
                "free_gb": 10.0,
                "price_per_min": 1.5,
                "price_per_sms": 0.5,
                "price_per_gb": 20.0,
            },
        },
        {
            "user_id": 102,
            "minutes_used": 100,
            "sms_used": 10,
            "gb_used": 2.0,
            "plan": {
                "base_fee": 100.0,
                "free_minutes": 200,
                "free_sms": 100,
                "free_gb": 5.0,
                "price_per_min": 1.0,
                "price_per_sms": 0.3,
                "price_per_gb": 15.0,
            },
        },
        {
            "user_id": 103,
            "minutes_used": 600,
            "sms_used": 120,
            "gb_used": 25.0,
            "plan": {
                "base_fee": 250.0,
                "free_minutes": 500,
                "free_sms": 100,
                "free_gb": 20.0,
                "price_per_min": 2.0,
                "price_per_sms": 0.6,
                "price_per_gb": 25.0,
            },
        },
    ]

    # Конфігурація політик через Callable
    accept_active = lambda r: r["minutes_used"] > 0 or r["gb_used"] > 0
    discount_10_percent = make_loyalty_bonus_policy(0.10)

    processor = make_tariff_processor(
        accept=accept_active,
        bonus_policy=discount_10_percent,
    )

    # Виклик чистого ядра та вивід
    result = processor(sample_records)
    render_report(result)


if __name__ == "__main__":
    run()