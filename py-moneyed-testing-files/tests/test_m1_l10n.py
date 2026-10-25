"""Member 1 - Module 3: format_money (src/moneyed/l10n.py).

Every call passes locale explicitly so the result does not depend on the computer's language settings.
"""
import pytest
from babel.core import UnknownLocaleError

from moneyed import EUR, JPY, USD, Money
from moneyed.l10n import format_money
from tests.helpers import load_csv

pytestmark = [pytest.mark.l10n, pytest.mark.order(3)]


@pytest.mark.regression
class TestFormatMoney:
    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "amount, expected",
        [
            ("0", "$0.00"),
            ("0.01", "$0.01"),
            ("999.99", "$999.99"),
            ("1000", "$1,000.00"),
            ("1234567.891", "$1,234,567.89"),
            ("-5", "-$5.00"),
        ],
        ids=["zero", "one_cent", "below_thousand", "thousand", "many_decimals", "negative"],
    )
    def test_usd_en_us(self, amount, expected):
        assert format_money(Money(amount, "USD"), locale="en_US") == expected

    @pytest.mark.boundary
    def test_half_cent_rounds_to_even(self):
        assert format_money(Money("0.005", "USD"), locale="en_US") == "$0.00"

    @pytest.mark.parametrize(
        "locale, expected",
        [
            ("en_US", "$1,000,000.00"),
            ("de_DE", "1.000.000,00\xa0$"),
            ("ur_PK", "$1,000,000.00"),
        ],
        ids=["english", "german", "urdu_pakistan"],
    )
    def test_locale_changes_the_separators(self, locale, expected):
        assert format_money(Money("1000000", "USD"), locale=locale) == expected

    @pytest.mark.parametrize(
        "format_type, expected",
        [("standard", "-$5.00"), ("accounting", "($5.00)")],
        ids=["standard", "accounting"],
    )
    def test_format_type_for_negative_amounts(self, format_type, expected):
        assert format_money(Money("-5", "USD"), locale="en_US", format_type=format_type) == expected

    def test_format_type_name(self):
        assert format_money(Money("5", "USD"), locale="en_US", format_type="name") == "5.00 US dollars"

    def test_currency_digits_true_uses_currency_rule(self):
        assert format_money(Money("500", "JPY"), locale="en_US", currency_digits=True) == "¥500"

    def test_currency_digits_false_uses_pattern_digits(self):
        assert format_money(Money("500", "JPY"), locale="en_US", currency_digits=False) == "¥500.00"

    def test_decimal_quantization_true_rounds(self):
        assert format_money(Money("2.0123", "USD"), locale="en_US") == "$2.01"

    def test_decimal_quantization_false_keeps_digits(self):
        assert format_money(Money("2.0123", "USD"), locale="en_US", decimal_quantization=False) == "$2.0123"

    def test_custom_pattern(self):
        # currency_digits=False so the pattern's own digit count (1) is used
        result = format_money(Money("5", "USD"), locale="en_US", format="#,##0.0 ¤", currency_digits=False)
        assert result == "5.0 $"

    def test_other_currency_symbols(self):
        assert format_money(Money("10", EUR), locale="en_US") == "€10.00"

    def test_unknown_locale_raises(self):
        with pytest.raises(UnknownLocaleError):
            format_money(Money("5", "USD"), locale="xx_YY")

    def test_str_uses_format_money(self):
        # str(Money) uses the default locale; we only check that the number is in the text.
        assert "5.00" in str(Money("5", "USD"))


# ---------------------------------------------------------------- CSV driven
@pytest.mark.csv
@pytest.mark.regression
@pytest.mark.parametrize("row", load_csv("format_money.csv"))
def test_format_money_from_csv(row):
    """Data-driven test: every row of tests/data/format_money.csv is one test."""
    money = Money(row["amount"], row["currency"])
    result = format_money(money, locale=row["locale"], format_type=row["format_type"])
    assert result == row["expected"]
