"""I/O shell: only this module prints results."""
from core import MobileResult, MobileUsage, calculate_monthly_cost, make_processor


def render_report(results: list[MobileResult]) -> None:
    for row in results:
        print(f"Номер: {row['mobile']}; тариф: {row['tariff']}; "
              f"місячна вартість: {row['monthly_cost']:.2f} грн")


def main() -> None:
    usages: list[MobileUsage] = [
        {'mobile': '0501112233', 'tariff': 'Standard', 'minutes': 120, 'sms': 40, 'traffic': 12.0},
        {'mobile': '0672223344', 'tariff': 'Standard', 'minutes': 80, 'sms': 70, 'traffic': 8.0},
        {'mobile': '0933334455', 'tariff': 'Archive', 'minutes': 40, 'sms': 10, 'traffic': 3.0},
    ]
    tariff_policy = lambda usage: calculate_monthly_cost(
        usage, base_cost=150.0, minutes_limit=100, minutes_price=1.5,
        sms_limit=50, sms_price=1.0, data_limit=10.0, traffic_price=20.0)
    bonus_policy = lambda cost: cost * 0.9  # 10% bonus discount
    accept = lambda usage: usage['tariff'] == 'Standard'
    processor = make_processor(accept=accept, tariff_policy=tariff_policy,
                               bonus_policy=bonus_policy)
    render_report(processor(usages))


if __name__ == '__main__':
    main()
