"""Pure mobile tariff calculations for laboratory work 1, variant 11."""
from typing import Callable, TypedDict


class MobileUsage(TypedDict):
    mobile: str
    tariff: str
    minutes: int
    sms: int
    traffic: float  # GB


class MobileResult(MobileUsage):
    monthly_cost: float


TariffFn = Callable[[MobileUsage], float]
BonusFn = Callable[[float], float]
FilterFn = Callable[[MobileUsage], bool]


def calculate_minutes_cost(minutes: int, limit: int, price: float) -> float:
    return max(0, minutes - limit) * price


def calculate_sms_cost(sms: int, limit: int, price: float) -> float:
    return max(0, sms - limit) * price


def calculate_traffic_cost(traffic: float, data_limit: float, price: float) -> float:
    return max(0.0, traffic - data_limit) * price


def calculate_monthly_cost(usage: MobileUsage, *, base_cost: float,
                           minutes_limit: int, minutes_price: float,
                           sms_limit: int, sms_price: float,
                           data_limit: float, traffic_price: float) -> float:
    return round(base_cost
                 + calculate_minutes_cost(usage['minutes'], minutes_limit, minutes_price)
                 + calculate_sms_cost(usage['sms'], sms_limit, sms_price)
                 + calculate_traffic_cost(usage['traffic'], data_limit, traffic_price), 2)


def with_monthly_cost(usage: MobileUsage, monthly_cost: float) -> MobileResult:
    return {**usage, 'monthly_cost': round(monthly_cost, 2)}


def filter_tariffs(usages: list[MobileUsage], accept: FilterFn) -> list[MobileUsage]:
    return [dict(usage) for usage in usages if accept(usage)]


def make_processor(*, accept: FilterFn, tariff_policy: TariffFn,
                   bonus_policy: BonusFn) -> Callable[[list[MobileUsage]], list[MobileResult]]:
    def process(usages: list[MobileUsage]) -> list[MobileResult]:
        return [with_monthly_cost(usage, max(0.0, bonus_policy(tariff_policy(usage))))
                for usage in usages if accept(usage)]
    return process
