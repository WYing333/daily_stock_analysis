"""Good fake service layer for BC testing."""

from src.repositories.bc_good_repo import load_probe_data


def get_probe_data(symbol: str) -> dict:
    data = load_probe_data(symbol)
    data["source"] = "service"
    return data
