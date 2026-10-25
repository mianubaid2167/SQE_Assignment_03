"""Member 1 - Module 1: Money class (src/moneyed/classes.py).

Techniques: ECP and BVA (see docs/test_design_notes.md).
"""
import warnings
from decimal import Decimal, DivisionByZero, InvalidOperation

import pytest

from moneyed import EUR, JPY, PKR, USD, Money
from moneyed.classes import CurrencyDoesNotExist, MoneyComparisonError
from tests.helpers import load_csv

pytestmark = [pytest.mark.money, pytest.mark.order(1)]


# ---------------------------------------------------------------- __init__
@pytest.mark.regression
class TestMoneyInit:
    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "amount, expected",
        [
            (5, Decimal("5")),
            ("5.50", Decimal("5.50")),
            (Decimal("7.25"), Decimal("7.25")),
            (1.5, Decimal("1.5")),
            (0, Decimal("0")),
        ],
        ids=["int", "str", "decimal", "float", "zero"],
    )
    def test_amount_types_become_decimal(self, amount, expected):
        money = Money(amount, "USD")
        assert isinstance(money.amount, Decimal)
        assert money.amount == expected

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "amount",
        ["0.01", "-0.01", 10**30, "0.0000001"],
        ids=["smallest_cent", "negative_cent", "very_large", "very_small"],
    )
    def test_boundary_amounts_are_kept_exactly(self, amount):
        assert Money(amount, "USD").amount == Decimal(str(amount))

    def test_lowercase_currency_code_is_accepted(self):
        assert Money(5, "usd").currency == USD

    def test_currency_object_is_accepted(self):
        assert Money(5, EUR).currency is EUR

    def test_amount_can_be_omitted_when_currency_is_keyword(self):
        assert Money(currency="USD").amount == Decimal("0.0")

    @pytest.mark.negative
    def test_unknown_currency_raises(self):
        with pytest.raises(CurrencyDoesNotExist):
            Money(5, "ABC")

    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.parametrize("code", ["US", "USDD"], ids=["2_letters", "4_letters"])
    def test_wrong_length_currency_code_raises(self, code):
        with pytest.raises(CurrencyDoesNotExist):
            Money(5, code)

    @pytest.mark.negative
    def test_missing_currency_raises_type_error(self):
        with pytest.raises(TypeError):
            Money(5)

    @pytest.mark.negative
    @pytest.mark.parametrize("amount", ["abc", None], ids=["text", "none"])
    def test_invalid_amount_raises(self, amount):
        with pytest.raises(InvalidOperation):
            Money(amount, "USD")


# ---------------------------------------------------------------- add / sub
@pytest.mark.regression
class TestMoneyAddSub:
    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "a, b, expected",
        [
            ("10", "5", "15"),
            ("10.25", "0.75", "11.00"),
            ("10", "-15", "-5"),
            ("0.01", "-0.01", "0"),
            ("1000000000", "1", "1000000001"),
        ],
        ids=["simple", "decimals", "negative", "zero_boundary", "large"],
    )
    def test_add_same_currency(self, a, b, expected):
        assert Money(a, "USD") + Money(b, "USD") == Money(expected, "USD")

    @pytest.mark.negative
    def test_add_different_currency_raises(self):
        with pytest.raises(TypeError):
            Money(10, "USD") + Money(5, "EUR")

    def test_add_plain_zero_returns_same_money(self):
        money = Money(10, "USD")
        assert money + 0 == money

    @pytest.mark.negative
    def test_add_non_zero_number_raises(self):
        with pytest.raises(TypeError):
            Money(10, "USD") + 5

    def test_sum_of_list_works(self):
        assert sum([Money(1, "USD"), Money(2, "USD"), Money(3, "USD")]) == Money(6, "USD")

    @pytest.mark.parametrize(
        "a, b, expected",
        [("10", "4", "6"), ("3", "10", "-7"), ("5", "5", "0"), ("0.02", "0.01", "0.01"), ("-5", "-5", "0")],
        ids=["simple", "negative_result", "equal", "one_cent", "both_negative"],
    )
    def test_subtract_same_currency(self, a, b, expected):
        assert Money(a, "PKR") - Money(b, "PKR") == Money(expected, "PKR")

    @pytest.mark.negative
    def test_subtract_different_currency_raises(self):
        with pytest.raises(TypeError):
            Money(10, "USD") - Money(5, "EUR")

    @pytest.mark.negative
    def test_number_minus_money_raises(self):
        with pytest.raises(TypeError):
            10 - Money(3, "USD")


# ---------------------------------------------------------------- mul / div
@pytest.mark.regression
class TestMoneyMulDiv:
    @pytest.mark.parametrize(
        "factor, expected",
        [(3, "30"), (0, "0"), (1, "10"), (-1, "-10"), (Decimal("0.5"), "5.0")],
        ids=["three", "zero", "one", "minus_one", "half"],
    )
    def test_multiply_by_number(self, factor, expected):
        assert Money(10, "USD") * factor == Money(expected, "USD")

    def test_rmul_works(self):
        assert 3 * Money(10, "USD") == Money(30, "USD")

    @pytest.mark.negative
    def test_multiply_two_money_raises(self):
        with pytest.raises(TypeError):
            Money(10, "USD") * Money(2, "USD")

    def test_multiply_by_float_warns(self):
        with pytest.warns(DeprecationWarning):
            Money(10, "USD") * 1.5

    @pytest.mark.parametrize(
        "divisor, expected",
        [(4, "2.5"), (1, "10"), (-2, "-5"), (Decimal("0.5"), "20"), (10, "1")],
        ids=["four", "one", "negative", "half", "ten"],
    )
    def test_divide_by_number(self, divisor, expected):
        assert Money(10, "USD") / divisor == Money(expected, "USD")

    @pytest.mark.negative
    def test_divide_by_zero_raises(self):
        with pytest.raises(DivisionByZero):
            Money(10, "USD") / 0

    def test_divide_money_by_money_gives_decimal(self):
        result = Money(10, "USD") / Money(4, "USD")
        assert result == Decimal("2.5")
        assert not isinstance(result, Money)

    @pytest.mark.negative
    def test_divide_different_currencies_raises(self):
        with pytest.raises(TypeError):
            Money(10, "USD") / Money(4, "EUR")

    @pytest.mark.negative
    def test_number_divided_by_money_raises(self):
        with pytest.raises(TypeError):
            10 / Money(4, "USD")

    def test_percentage_with_rmod(self):
        assert 5 % Money(200, "USD") == Money(10, "USD")


# ---------------------------------------------------------------- round
@pytest.mark.regression
class TestMoneyRound:
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "amount, ndigits, expected",
        [
            ("2.345", 2, "2.34"),  # exactly half: rounds to the even digit
            ("2.355", 2, "2.36"),
            ("2.5", 0, "2"),
            ("3.5", 0, "4"),
            ("-2.345", 2, "-2.34"),
            ("2.349", 2, "2.35"),
            ("2.31", 1, "2.3"),
        ],
        ids=["half_down_even", "half_up_even", "2_5", "3_5", "negative", "just_above_half", "one_digit"],
    )
    def test_round_values(self, amount, ndigits, expected):
        assert Money(amount, "USD").round(ndigits) == Money(expected, "USD")

    def test_round_none_is_treated_as_zero_digits(self):
        assert Money("2.5", "USD").round(None) == Money("2", "USD")

    def test_round_keeps_currency(self):
        assert Money("2.5", "EUR").round(0).currency == EUR

    def test_round_default_is_zero_digits(self):
        assert Money("7.6", "USD").round() == Money("8", "USD")


# ---------------------------------------------------------------- comparison
@pytest.mark.regression
class TestMoneyComparison:
    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "a, b, less, equal, greater",
        [
            ("5", "10", True, False, False),
            ("10", "10", False, True, False),
            ("10.00", "10", False, True, False),
            ("10.01", "10", False, False, True),
            ("-1", "0", True, False, False),
        ],
        ids=["smaller", "equal", "same_value_other_scale", "one_cent_bigger", "negative"],
    )
    def test_same_currency_comparison(self, a, b, less, equal, greater):
        ma, mb = Money(a, "USD"), Money(b, "USD")
        assert (ma < mb) is less
        assert (ma == mb) is equal
        assert (ma > mb) is greater
        assert (ma <= mb) is (less or equal)
        assert (ma >= mb) is (greater or equal)

    def test_different_currency_is_not_equal(self):
        assert Money(10, "USD") != Money(10, "EUR")

    @pytest.mark.negative
    def test_different_currency_less_than_raises(self):
        with pytest.raises(TypeError):
            Money(10, "USD") < Money(10, "EUR")

    @pytest.mark.negative
    def test_compare_with_number_raises(self):
        with pytest.raises(MoneyComparisonError):
            Money(10, "USD") < 10

    def test_equal_to_number_is_false(self):
        assert (Money(10, "USD") == 10) is False


# ---------------------------------------------------------------- sub unit
@pytest.mark.regression
class TestMoneySubUnit:
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "amount, currency, expected",
        [
            ("12.34", "USD", 1234),
            ("0", "USD", 0),
            ("0.01", "USD", 1),
            ("1", "USD", 100),
            ("500", "JPY", 500),
            ("1234.5", "PKR", 123450),
        ],
        ids=["usd", "zero", "one_cent", "one_dollar", "yen_no_subunit", "pkr"],
    )
    def test_get_amount_in_sub_unit(self, amount, currency, expected):
        assert Money(amount, currency).get_amount_in_sub_unit() == expected


# ---------------------------------------------------------------- whole class
@pytest.mark.regression
class TestMoneyClass:
    def test_repr_shows_amount_and_currency(self):
        assert repr(Money("5.50", "USD")) == "Money('5.50', 'USD')"

    def test_equal_money_has_equal_hash(self):
        assert hash(Money(10, "USD")) == hash(Money("10.00", "USD"))

    def test_money_can_be_used_in_a_set(self):
        assert len({Money(1, "USD"), Money(1, "USD"), Money(2, "USD")}) == 2

    @pytest.mark.parametrize(
        "amount, expected",
        [("0", False), ("0.00", False), ("0.01", True), ("-3", True)],
        ids=["zero", "zero_two_places", "cent", "negative"],
    )
    def test_bool(self, amount, expected):
        assert bool(Money(amount, "USD")) is expected

    def test_negation(self):
        assert -Money(3, "USD") == Money(-3, "USD")

    def test_absolute_value(self):
        assert abs(Money(-3, "USD")) == Money(3, "USD")

    def test_unary_plus_returns_equal_money(self):
        assert +Money(3, "USD") == Money(3, "USD")

    def test_currency_zero_is_zero_money(self):
        assert PKR.zero == Money(0, "PKR")

    def test_class_keeps_type_after_operations(self):
        class MyMoney(Money):
            pass

        assert isinstance(MyMoney(1, "USD") + MyMoney(2, "USD"), MyMoney)


# ---------------------------------------------------------------- CSV driven
@pytest.mark.csv
@pytest.mark.regression
@pytest.mark.parametrize("row", load_csv("money_operations.csv"))
def test_money_operations_from_csv(row):
    """Data-driven test: every row of tests/data/money_operations.csv is one test."""
    a = Money(row["amount_a"], row["currency_a"])
    op = row["operation"]
    error = {"TypeError": TypeError, "DivisionByZero": DivisionByZero}.get(row["expected_error"])

    def run():
        if op == "add":
            return a + Money(row["amount_b"], row["currency_b"])
        if op == "sub":
            return a - Money(row["amount_b"], row["currency_b"])
        if op == "mul":
            return a * Decimal(row["amount_b"])
        if op == "div_number":
            return a / Decimal(row["amount_b"])
        if op == "div_money":
            return a / Money(row["amount_b"], row["currency_b"])
        raise AssertionError(f"unknown operation {op}")

    if error:
        with pytest.raises(error):
            run()
        return

    result = run()
    if op == "div_money":
        assert result == Decimal(row["expected_amount"])
    else:
        assert result == Money(row["expected_amount"], row["expected_currency"])
