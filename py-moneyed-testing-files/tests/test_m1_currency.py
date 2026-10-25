"""Member 1 - Module 2: Currency class and lookup functions (src/moneyed/classes.py)."""
import pytest

from moneyed import EUR, PKR, USD, Currency, get_currency
from moneyed.classes import (
    CurrencyDoesNotExist,
    get_currencies_of_country,
    list_all_currencies,
)
from tests.helpers import load_csv

pytestmark = [pytest.mark.currency, pytest.mark.order(2)]


# ---------------------------------------------------------------- get_currency
@pytest.mark.regression
class TestGetCurrency:
    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "code, expected",
        [("USD", USD), ("EUR", EUR), ("PKR", PKR), ("JPY", get_currency("JPY")), ("GBP", get_currency("GBP"))],
        ids=["usd", "eur", "pkr", "jpy", "gbp"],
    )
    def test_valid_code(self, code, expected):
        assert get_currency(code) == expected

    @pytest.mark.parametrize(
        "iso, expected",
        [(840, USD), ("840", USD), (978, EUR), ("586", PKR), (586, PKR)],
        ids=["usd_int", "usd_str", "eur", "pkr_str", "pkr_int"],
    )
    def test_valid_iso_number(self, iso, expected):
        assert get_currency(iso=iso) == expected

    @pytest.mark.negative
    @pytest.mark.parametrize(
        "code",
        ["ABC", "usd", "", "US", "USDD", "XXX1"],
        ids=["unknown", "lowercase", "empty", "2_letters", "4_letters", "digit_in_code"],
    )
    def test_invalid_code_raises(self, code):
        with pytest.raises(CurrencyDoesNotExist):
            get_currency(code)

    @pytest.mark.negative
    @pytest.mark.parametrize("iso", [99999, "abc", 1], ids=["too_big", "text", "unused_number"])
    def test_invalid_iso_raises(self, iso):
        with pytest.raises(CurrencyDoesNotExist):
            get_currency(iso=iso)

    @pytest.mark.negative
    def test_no_arguments_raises(self):
        with pytest.raises(CurrencyDoesNotExist):
            get_currency()

    def test_error_message_contains_the_code(self):
        with pytest.raises(CurrencyDoesNotExist, match="ABC"):
            get_currency("ABC")


# ---------------------------------------------------------------- get_currencies_of_country
@pytest.mark.regression
class TestGetCurrenciesOfCountry:
    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "country, expected_code",
        [("PK", "PKR"), ("pk", "PKR"), ("JP", "JPY"), ("GB", "GBP"), ("DE", "EUR")],
        ids=["pakistan", "lowercase", "japan", "uk", "germany"],
    )
    def test_country_with_one_currency(self, country, expected_code):
        assert get_currency(expected_code) in get_currencies_of_country(country)

    def test_pakistan_has_exactly_pkr(self):
        assert get_currencies_of_country("PK") == [PKR]

    def test_country_with_several_currencies(self):
        codes = [c.code for c in get_currencies_of_country("CH")]
        assert {"CHF", "CHE", "CHW"} <= set(codes)

    def test_result_is_sorted_by_code(self):
        result = get_currencies_of_country("CH")
        assert result == sorted(result)

    @pytest.mark.negative
    def test_empty_country_gives_empty_list(self):
        assert get_currencies_of_country("") == []

    def test_returns_currency_objects(self):
        assert all(isinstance(c, Currency) for c in get_currencies_of_country("US"))


# ---------------------------------------------------------------- list_all_currencies
@pytest.mark.regression
class TestListAllCurrencies:
    def test_contains_common_currencies(self):
        assert {USD, EUR, PKR} <= set(list_all_currencies())

    def test_is_sorted_by_code(self):
        codes = [c.code for c in list_all_currencies()]
        assert codes == sorted(codes)

    def test_has_no_duplicates(self):
        codes = [c.code for c in list_all_currencies()]
        assert len(codes) == len(set(codes))

    def test_has_many_entries(self):
        assert len(list_all_currencies()) > 100

    def test_every_entry_has_three_letter_code(self):
        assert all(len(c.code) == 3 for c in list_all_currencies())


# ---------------------------------------------------------------- Currency class
@pytest.mark.regression
class TestCurrencyClass:
    def test_same_code_is_equal(self):
        assert get_currency("USD") == USD

    def test_different_code_is_not_equal(self):
        assert USD != EUR

    def test_equal_currencies_have_equal_hash(self):
        assert hash(USD) == hash(get_currency("USD"))

    def test_currency_works_as_dict_key(self):
        assert {USD: "dollar"}[get_currency("USD")] == "dollar"

    def test_repr_is_the_code(self):
        assert repr(PKR) == "PKR"

    def test_ordering_is_by_code(self):
        assert EUR < USD
        assert USD >= EUR

    def test_zero_property_gives_zero_money(self):
        assert USD.zero.amount == 0
        assert USD.zero.currency == USD

    def test_name_in_us_locale(self):
        assert USD.name == "US Dollar"

    def test_get_name_in_another_locale(self):
        assert USD.get_name("de_DE") == "US-Dollar"

    def test_country_codes_of_pkr(self):
        assert PKR.country_codes == ["PK"]

    def test_custom_currency_object(self):
        custom = Currency(code="ZZZ", numeric="999", sub_unit=10, name="Test Coin")
        assert custom.code == "ZZZ"
        assert custom.sub_unit == 10
        assert custom.name == "Test Coin"


# ---------------------------------------------------------------- CSV driven
@pytest.mark.csv
@pytest.mark.regression
@pytest.mark.parametrize("row", load_csv("currency_lookup.csv"))
def test_get_currency_from_csv(row):
    """Data-driven test: every row of tests/data/currency_lookup.csv is one test."""
    kwargs = {"iso": row["iso"]} if row["iso"] else {}
    args = (row["code"],) if row["code"] else ()
    if row["expected_error"]:
        with pytest.raises(CurrencyDoesNotExist):
            get_currency(*args, **kwargs)
    else:
        assert get_currency(*args, **kwargs).code == row["expected_code"]
