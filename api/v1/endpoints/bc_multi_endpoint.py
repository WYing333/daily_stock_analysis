"""Fake API layer for multi-violation test.

Expected violation:
- api -> data
"""

from src.repositories.bc_multi_repo import load_multi_data


def bc_multi_endpoint(symbol: str) -> dict:
    return load_multi_data(symbol)
