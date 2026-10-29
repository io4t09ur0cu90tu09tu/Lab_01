from copy import deepcopy

from core import (calculate_minutes_cost, calculate_sms_cost,
                  calculate_traffic_cost, calculate_monthly_cost,
                  filter_tariffs, make_processor)


def sample():
    return [{'mobile': '0501112233', 'tariff': 'Standard', 'minutes': 120,
             'sms': 40, 'traffic': 12.0}]


def policy(usage):
    return calculate_monthly_cost(usage, base_cost=150, minutes_limit=100,
                                  minutes_price=1.5, sms_limit=50, sms_price=1,
                                  data_limit=10, traffic_price=20)


def processor():
    return make_processor(accept=lambda u: u['tariff'] == 'Standard',
                          tariff_policy=policy, bonus_policy=lambda cost: cost * 0.9)


def test_calculations():
    assert calculate_minutes_cost(120, 100, 1.5) == 30
    assert calculate_sms_cost(40, 50, 1) == 0
    assert calculate_traffic_cost(12, 10, 20) == 40
    assert policy(sample()[0]) == 220


def test_referential_transparency():
    usages = sample()
    assert processor()(usages) == processor()(usages)


def test_no_mutation():
    usages = sample()
    before = deepcopy(usages)
    processor()(usages)
    assert usages == before
    assert 'monthly_cost' not in usages[0]


def test_callable_policies():
    result = processor()(sample())
    assert result[0]['monthly_cost'] == 198
    assert result[0]['tariff'] == 'Standard'


def test_filter_tariffs():
    usages = sample() + [{'mobile': '1', 'tariff': 'Archive', 'minutes': 0,
                          'sms': 0, 'traffic': 0.0}]
    filtered = filter_tariffs(usages, lambda u: u['tariff'] == 'Standard')
    assert len(filtered) == 1
    assert filtered[0] is not usages[0]
