"""Simple duties/taxes estimator for international shipments.

This is a planning tool and not legal/tax advice.
Actual import charges can vary by HS code, trade agreements,
carrier fees, and customs discretion.
"""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CountryRule:
    country: str
    currency: str
    de_minimis_value: float
    vat_threshold: float
    default_vat_rate: float


@dataclass(frozen=True)
class EstimateInputs:
    country: str
    item_value: float
    shipping_cost: float
    insurance_cost: float
    duty_rate: float
    vat_rate: float
    brokerage_fee: float
    handling_fee: float
    vat_includes_shipping: bool


@dataclass(frozen=True)
class EstimateResult:
    customs_value: float
    dutiable_value: float
    duty_amount: float
    vat_base: float
    vat_amount: float
    total_import_charges: float
    landed_cost: float


def load_country_rules(path: str | Path) -> dict[str, CountryRule]:
    raw = json.loads(Path(path).read_text())
    rules: dict[str, CountryRule] = {}
    for code, payload in raw.items():
        rules[code.upper()] = CountryRule(
            country=payload["country"],
            currency=payload["currency"],
            de_minimis_value=float(payload["de_minimis_value"]),
            vat_threshold=float(payload["vat_threshold"]),
            default_vat_rate=float(payload["default_vat_rate"]),
        )
    return rules


def estimate_import_charges(inputs: EstimateInputs, rule: CountryRule) -> EstimateResult:
    customs_value = inputs.item_value + inputs.insurance_cost
    if inputs.vat_includes_shipping:
        customs_value += inputs.shipping_cost

    dutiable_value = max(customs_value - rule.de_minimis_value, 0.0)
    duty_amount = dutiable_value * inputs.duty_rate

    vat_base = inputs.item_value + inputs.insurance_cost + duty_amount
    if inputs.vat_includes_shipping:
        vat_base += inputs.shipping_cost

    vat_applies = vat_base >= rule.vat_threshold
    vat_amount = vat_base * inputs.vat_rate if vat_applies else 0.0

    total_import_charges = (
        duty_amount + vat_amount + inputs.brokerage_fee + inputs.handling_fee
    )
    landed_cost = (
        inputs.item_value
        + inputs.shipping_cost
        + inputs.insurance_cost
        + total_import_charges
    )

    return EstimateResult(
        customs_value=round(customs_value, 2),
        dutiable_value=round(dutiable_value, 2),
        duty_amount=round(duty_amount, 2),
        vat_base=round(vat_base, 2),
        vat_amount=round(vat_amount, 2),
        total_import_charges=round(total_import_charges, 2),
        landed_cost=round(landed_cost, 2),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Estimate duties/taxes for international shipments"
    )
    parser.add_argument("--country", required=True, help="ISO country code, e.g. CA")
    parser.add_argument("--item-value", type=float, required=True)
    parser.add_argument("--shipping-cost", type=float, default=0.0)
    parser.add_argument("--insurance-cost", type=float, default=0.0)
    parser.add_argument("--duty-rate", type=float, required=True, help="0.05 for 5%")
    parser.add_argument(
        "--vat-rate",
        type=float,
        default=None,
        help="Override VAT/GST rate; if omitted, country default is used",
    )
    parser.add_argument("--brokerage-fee", type=float, default=0.0)
    parser.add_argument("--handling-fee", type=float, default=0.0)
    parser.add_argument(
        "--vat-includes-shipping",
        action="store_true",
        help="Include shipping in customs + VAT base",
    )
    parser.add_argument(
        "--rules-file",
        default="country_rules.json",
        help="Path to country rules JSON",
    )
    return parser


def _result_to_dict(result: EstimateResult) -> dict[str, Any]:
    return {
        "customs_value": result.customs_value,
        "dutiable_value": result.dutiable_value,
        "duty_amount": result.duty_amount,
        "vat_base": result.vat_base,
        "vat_amount": result.vat_amount,
        "total_import_charges": result.total_import_charges,
        "landed_cost": result.landed_cost,
    }


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    rules = load_country_rules(args.rules_file)
    code = args.country.upper()
    if code not in rules:
        available = ", ".join(sorted(rules))
        raise SystemExit(f"Unknown country code '{code}'. Available: {available}")

    rule = rules[code]
    vat_rate = rule.default_vat_rate if args.vat_rate is None else args.vat_rate
    inputs = EstimateInputs(
        country=code,
        item_value=args.item_value,
        shipping_cost=args.shipping_cost,
        insurance_cost=args.insurance_cost,
        duty_rate=args.duty_rate,
        vat_rate=vat_rate,
        brokerage_fee=args.brokerage_fee,
        handling_fee=args.handling_fee,
        vat_includes_shipping=args.vat_includes_shipping,
    )

    result = estimate_import_charges(inputs, rule)
    print(json.dumps({"country": code, "currency": rule.currency, **_result_to_dict(result)}, indent=2))


if __name__ == "__main__":
    main()
