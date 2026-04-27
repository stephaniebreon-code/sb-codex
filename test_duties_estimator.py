from duties_estimator import CountryRule, EstimateInputs, estimate_import_charges


def test_estimate_with_de_minimis_and_fees() -> None:
    rule = CountryRule(
        country="Canada",
        currency="CAD",
        de_minimis_value=20,
        vat_threshold=0,
        default_vat_rate=0.05,
    )
    inputs = EstimateInputs(
        country="CA",
        item_value=200,
        shipping_cost=30,
        insurance_cost=0,
        duty_rate=0.08,
        vat_rate=0.05,
        brokerage_fee=9.95,
        handling_fee=4,
        vat_includes_shipping=True,
    )

    result = estimate_import_charges(inputs, rule)

    assert result.customs_value == 230.00
    assert result.dutiable_value == 210.00
    assert result.duty_amount == 16.80
    assert result.vat_base == 246.80
    assert result.vat_amount == 12.34
    assert result.total_import_charges == 43.09
    assert result.landed_cost == 273.09


def test_estimate_below_vat_threshold() -> None:
    rule = CountryRule(
        country="Example",
        currency="USD",
        de_minimis_value=0,
        vat_threshold=150,
        default_vat_rate=0.20,
    )
    inputs = EstimateInputs(
        country="EX",
        item_value=100,
        shipping_cost=10,
        insurance_cost=0,
        duty_rate=0,
        vat_rate=0.20,
        brokerage_fee=0,
        handling_fee=0,
        vat_includes_shipping=False,
    )

    result = estimate_import_charges(inputs, rule)

    assert result.vat_base == 100.00
    assert result.vat_amount == 0.00
    assert result.total_import_charges == 0.00
