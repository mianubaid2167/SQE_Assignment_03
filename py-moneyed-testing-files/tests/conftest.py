"""Shared pytest setup for the extra test suite.

Babel reads the default locale from the OS environment when it is imported.
On Windows there is none, which makes some tests fail with
"Empty locale identifier value: None". We set a default BEFORE moneyed/babel
is imported, so the tests behave the same on every machine.
"""
import os

os.environ.setdefault("LANG", "en_US.UTF-8")
