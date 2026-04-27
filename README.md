# International Duties/Taxes Estimator

A lightweight Python estimator you can run before buying a shipping label in third-party software.

> This is an estimate only. Real import charges depend on HS code classification, origin rules,
> carrier-specific fees, customs rulings, and destination-country updates.

## What it calculates

Given a destination, item value, shipping cost, and rates, it estimates:

- Customs value
- Dutiable value (after de minimis)
- Duty amount
- VAT/GST base and VAT/GST amount
- Total import charges (duty + VAT + fixed fees)
- Landed cost

## Quick start

```bash
python3 duties_estimator.py \
  --country CA \
  --item-value 200 \
  --shipping-cost 30 \
  --duty-rate 0.08 \
  --brokerage-fee 9.95 \
  --handling-fee 4 \
  --vat-includes-shipping
```

Example output:

```json
{
  "country": "CA",
  "currency": "CAD",
  "customs_value": 230.0,
  "dutiable_value": 210.0,
  "duty_amount": 16.8,
  "vat_base": 246.8,
  "vat_amount": 12.34,
  "total_import_charges": 43.09,
  "landed_cost": 273.09
}
```

## Country rules file

Rules live in `country_rules.json` and currently include sample baselines for:

- `CA`
- `GB`
- `AU`
- `DE`

You can add more countries or override VAT rate at runtime with `--vat-rate`.

## Run tests

```bash
python3 -m pytest -q
```
