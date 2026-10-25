# How to run the tests

## 1. Setup (Windows)

```
python -m venv venv
venv\Scripts\activate
pip install -e .
pip install pytest pytest-xdist pytest-order pytest-cov babel
```

Mac / Linux: use `source venv/bin/activate` instead of `venv\Scripts\activate`.

## 2. Run everything

```
pytest
```

Tests run in a fixed order (see section 5). One old test in the original project
(`test_all_babel_currencies`) fails with new Babel versions because Babel now knows two
newer currencies (XCG, ZWG). This is not caused by our tests.

## 3. Test groups (markers)

| Group | Command | What runs |
|-------|---------|-----------|
| smoke | `pytest -m smoke` | small set of basic checks |
| regression | `pytest -m regression` | full set |
| money | `pytest -m money` | Money class tests |
| currency | `pytest -m currency` | Currency class and lookup tests |
| l10n | `pytest -m l10n` | format_money tests |
| csv | `pytest -m csv` | data-driven tests that read `tests/data/*.csv` |
| boundary | `pytest -m boundary` | BVA tests |
| negative | `pytest -m negative` | tests that expect an error |

Groups can be combined: `pytest -m "money and csv"`, `pytest -m "regression and not csv"`.

## 4. Run in parallel

```
pytest -n auto --dist loadfile
```

`-n auto` uses all CPU cores. `--dist loadfile` keeps all tests of one file on the same worker,
so each module (suite) is run as a unit. Different suites in parallel:

```
pytest -n 3 tests/test_m1_money.py tests/test_m1_currency.py tests/test_m1_l10n.py --dist loadfile
```

## 5. Execution order

`pytest-order` is used. Every file sets its group order with `pytest.mark.order(n)`:

| Order | File |
|-------|------|
| 1 | `tests/test_m1_money.py` (Money class) |
| 2 | `tests/test_m1_currency.py` (Currency and lookup) |
| 3 | `tests/test_m1_l10n.py` (format_money) |

Inside each file tests run top to bottom: init, add/sub, mul/div, round, comparison,
sub unit, whole class, then CSV tests. Order is only guaranteed when running without `-n`.

## 6. Data-driven tests (parameterization)

* `@pytest.mark.parametrize` is used in all test files.
* Test data is read from CSV files in `tests/data/` by `tests/helpers.py`:
  * `money_operations.csv`
  * `currency_lookup.csv`
  * `format_money.csv`
* To add a test, add a row to the CSV file. No Python change is needed.

## 7. Coverage report (optional)

```
pytest --cov=moneyed --cov-report=term-missing
```

## 8. Files added for this assignment

| File | Purpose |
|------|---------|
| `docs/test_design_notes.md` | ECP and BVA notes (Task 2) |
| `docs/test_cases.xlsx` | Excel test cases (Task 3) |
| `tests/test_m1_*.py` | Automated tests (Task 2) |
| `tests/data/*.csv` | External test data (Task 3) |
| `tests/conftest.py`, `tests/helpers.py` | Shared setup and CSV reader |
| `pytest.ini` | Markers and settings (Task 4) |
| `README_TESTING.md` | This file |
| `docs/summary_report.md` | Summary report |

## 9. Adding tests for another team member

Copy the pattern: create `tests/test_m2_<module>.py` with your own tests, add
`pytestmark = [pytest.mark.<module>, pytest.mark.order(n)]` at the top, and commit from your own account.
