"""Good fake API layer for BC testing."""

from src.services.bc_good_service import get_probe_data


def bc_good_endpoint(symbol: str) -> dict:
    return get_probe_data(symbol)
