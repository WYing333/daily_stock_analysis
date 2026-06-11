"""Good fake repository layer for BC testing."""

def load_probe_data(symbol: str) -> dict:
    return {"symbol": symbol, "source": "repo"}
