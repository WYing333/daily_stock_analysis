"""Fake data layer for API-to-data violation test."""

def load_direct_data(symbol: str) -> dict:
    return {"symbol": symbol, "source": "data"}
