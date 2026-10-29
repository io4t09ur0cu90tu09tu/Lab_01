from copy import deepcopy
import pytest
from core import (
    UsageRecord,
    calculate_extra_minutes_cost,
    calculate_extra_gb_cost,
    make_tariff_processor,
    make_loyalty_bonus_policy,
)


@pytest.fixture
def sample_records() -> list[UsageRecord]:
    return [
        {
            "user_id": 1,
            "minutes_used": 120,
            "sms_used": 15,
            "gb_used": 6.0,
            "plan": {
                "base_fee": 100.0,
                "free_minutes": 100,
                "free_sms": 10,
                "free_gb": 5.0,
                "price_per_min": 2.0,
                "price_per_sms": 1.0,
                "price_per_gb": 10.0,
            },
        }
    ]


def test_referential_transparency(sample_records):
    """Перевірка детермінованості: однаковий вхід дає однаковий вихід."""
    processor = make_tariff_processor(
        accept=lambda r: True, bonus_policy=make_loyalty_bonus_policy(0.1)
    )

    r1 = processor(sample_records)
    r2 = processor(sample_records)

    assert r1 == r2


def test_no_mutation(sample_records):
    """Перевірка відсутності мутацій вхідних даних."""
    original = deepcopy(sample_records)
    processor = make_tariff_processor(
        accept=lambda r: True, bonus_policy=lambda x: x
    )

    processor(sample_records)

    assert sample_records == original


def test_callable_policies(sample_records):
    """Перевірка коректності обчислень із застосуванням політик."""
    # Очікувані обчислення:
    # base = 100
    # extra min = (120 - 100) * 2.0 = 40
    # extra sms = (15 - 10) * 1.0 = 5
    # extra gb = (6.0 - 5.0) * 10.0 = 10
    # subtotal = 100 + 40 + 5 + 10 = 155
    # bonus_policy (20% discount) -> 155 * 0.8 = 124.0

    processor = make_tariff_processor(
        accept=lambda r: r["user_id"] == 1,
        bonus_policy=make_loyalty_bonus_policy(0.20),
    )

    result = processor(sample_records)
    processed_rec = result["records"][0]

    assert result["count"] == 1
    assert processed_rec["monthly_cost"] == 124.0
    assert processed_rec["extra_minutes_cost"] == 40.0
    assert processed_rec["extra_gb_cost"] == 10.0


def test_extra_cost_calculators(sample_records):
    """Тест окремих чистих функцій."""
    rec = sample_records[0]
    assert calculate_extra_minutes_cost(rec) == 40.0
    assert calculate_extra_gb_cost(rec) == 10.0