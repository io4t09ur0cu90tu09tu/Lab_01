from copy import deepcopy
import pytest
from core import (
    UsageRecord,
    calculate_minutes_cost,
    calculate_sms_cost,
    calculate_traffic_cost,
    calculate_monthly_cost,
    filter_tariffs,
    make_processor,
)


@pytest.fixture
def sample_records() -> list[UsageRecord]:
    return [
        {
            "user_id": 1,
            "minutes_used": 120,
            "sms_used": 60,
            "gb_used": 12.0,
            "plan": {
                "base_fee": 150.0,
                "free_minutes": 100,
                "free_sms": 50,
                "free_gb": 10.0,
                "price_per_min": 2.0,
                "price_per_sms": 1.0,
                "price_per_gb": 10.0,
            },
        }
    ]


def test_referential_transparency(sample_records):
    """Перевірка детермінованості (референтної прозорості)[cite: 9]."""
    processor = make_processor(
        filter_fn=lambda r: True, bonus_policy=lambda x: x
    )

    r1 = processor(sample_records)
    r2 = processor(sample_records)

    assert r1 == r2


def test_no_mutation(sample_records):
    """Перевірка відсутності мутацій вхідних даних[cite: 9]."""
    original = deepcopy(sample_records)
    processor = make_processor(
        filter_fn=lambda r: True, bonus_policy=lambda x: x
    )

    processor(sample_records)

    assert sample_records == original


def test_individual_calculations(sample_records):
    """Тест окремих чистих функцій розрахунку."""
    rec = sample_records[0]
    assert calculate_minutes_cost(rec) == 40.0  # (120 - 100) * 2.0
    assert calculate_sms_cost(rec) == 10.0      # (60 - 50) * 1.0
    assert calculate_traffic_cost(rec) == 20.0  # (12.0 - 10.0) * 10.0
    
    subtotal = 150.0 + 40.0 + 10.0 + 20.0
    assert calculate_monthly_cost(150.0, 40.0, 10.0, 20.0, lambda x: x) == subtotal