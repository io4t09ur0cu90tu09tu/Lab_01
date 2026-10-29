"""Оболонка для роботи з I/O та виклику чистого ядра (Мобільний тариф)[cite: 9]."""

from typing import List
from core import UsageRecord, make_processor


def render_report(result: dict[str, object]) -> None:
    """Функція для відображення результатів (I/O, print)[cite: 9]."""
    print("=== ЗВІТ РОЗРАХУНКУ МОБІЛЬНИХ ТАРИФІВ (Варіант 11) ===")
    print(f"Опрацьовано записів: {result['count']}")
    print("-" * 65)

    records = result.get("records", [])
    if isinstance(records, list):
        for rec in records:
            print(
                f"Користувач ID: {rec['user_id']} | "
                f"Базова плата: {rec['plan']['base_fee']} грн | "
                f"Понад ліміт: {rec['extra_minutes_cost'] + rec['extra_sms_cost'] + rec['extra_traffic_cost']:.2f} грн | "
                f"Місячна вартість (monthly cost): {rec['monthly_cost']} грн"
            )

    print("-" * 65)
    print(f"Загальний дохід (Revenue): {result['revenue']} грн\n")


def run() -> None:
    # Демонстраційні умови: абонплата 150 грн, ліміт: 100 хв, 50 SMS, 10 ГБ
    sample_records: List[UsageRecord] = [
        {
            "user_id": 101,
            "minutes_used": 150,  # 50 хв понад ліміт
            "sms_used": 60,     # 10 SMS понад ліміт
            "gb_used": 12.0,    # 2 ГБ понад ліміт
            "plan": {
                "base_fee": 150.0,
                "free_minutes": 100,
                "free_sms": 50,
                "free_gb": 10.0,
                "price_per_min": 1.5,
                "price_per_sms": 0.5,
                "price_per_gb": 20.0,
            },
        },
        {
            "user_id": 102,
            "minutes_used": 80,
            "sms_used": 20,
            "gb_used": 5.0,
            "plan": {
                "base_fee": 150.0,
                "free_minutes": 100,
                "free_sms": 50,
                "free_gb": 10.0,
                "price_per_min": 1.5,
                "price_per_sms": 0.5,
                "price_per_gb": 20.0,
            },
        },
    ]

    # Використання фільтра (filter, limit) та політики бонусів (bonus) через Callable[cite: 9]
    filter_active_users = lambda r: r["minutes_used"] > 0 or r["gb_used"] > 0
    apply_bonus_policy = lambda cost: cost * 0.95  # 5% знижка лояльності

    processor = make_processor(
        filter_fn=filter_active_users,
        bonus_policy=apply_bonus_policy,
    )

    result = processor(sample_records)
    render_report(result)


if __name__ == "__main__":
    run()