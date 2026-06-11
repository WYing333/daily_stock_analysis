"""Fake API endpoint imported by data layer for violation test."""

def endpoint_helper(symbol: str) -> dict:
    return {"symbol": symbol, "source": "api"}
