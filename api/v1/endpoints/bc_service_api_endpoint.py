"""Fake API endpoint imported by service for violation test."""

def api_helper(symbol: str) -> dict:
    return {"symbol": symbol, "source": "api"}
