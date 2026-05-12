import pandas as pd
import pytest

from stackoverflow_analytics.tousd import (
    build_update_payload,
    calculate_salary_usd,
    conv_usd,
    extract_currency_code,
)


@pytest.mark.parametrize(
    ("raw_currency", "expected"),
    [
        ("USD\tUnited States dollar", "USD"),
        ("EUR European Euro", "EUR"),
        (None, None),
    ],
)
def test_extract_currency_code(raw_currency, expected):
    assert extract_currency_code(raw_currency) == expected


def test_conv_usd_handles_known_unknown_and_missing_values():
    assert conv_usd("USD", 100) == 100
    assert conv_usd("EUR", 100) == 109
    assert conv_usd("UNKNOWN", 100) is None
    assert conv_usd(None, 100) is None


def test_calculate_salary_usd_filters_outliers_and_invalid_values():
    source = pd.DataFrame(
        [
            {"ResponseId": 1, "Currency": "USD\tUnited States dollar", "CompTotal": "100000"},
            {"ResponseId": 2, "Currency": "USD\tUnited States dollar", "CompTotal": "50"},
            {"ResponseId": 3, "Currency": "USD\tUnited States dollar", "CompTotal": "900000"},
            {"ResponseId": 4, "Currency": "UNKNOWN", "CompTotal": "100000"},
        ]
    )

    result = calculate_salary_usd(source)

    assert result["ResponseId"].tolist() == [1]
    assert result["salaryusd"].tolist() == [100000]


def test_calculate_salary_usd_reports_missing_required_columns():
    source = pd.DataFrame([{"ResponseId": 1}])

    with pytest.raises(ValueError, match="Missing required columns"):
        calculate_salary_usd(source)


def test_build_update_payload_uses_response_id_and_salary():
    source = pd.DataFrame([{"ResponseId": 1, "salaryusd": 100000.0}])

    assert build_update_payload(source) == [{"rid": 1, "usd": 100000.0}]
