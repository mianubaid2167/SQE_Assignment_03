"""Small helper that turns a CSV file into pytest parameters (data-driven tests)."""
import csv
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent / "data"


def load_csv(name):
    """Read tests/data/<name> and return a list of pytest.param, one per row.

    The first column of every file is the test id, shown in the pytest report.
    Empty cells are returned as None.
    """
    params = []
    with open(DATA_DIR / name, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            test_id = row.pop("test_id")
            values = {key: (value if value != "" else None) for key, value in row.items()}
            params.append(pytest.param(values, id=test_id))
    return params
