"""Fake API layer that directly imports data layer.

Expected violation:
- api -> data
"""

from src.repositories.bc_api_data_repo import load_direct_data


def bc_api_data_endpoint(symbol: str) -> dict:
    return load_direct_data(symbol)
