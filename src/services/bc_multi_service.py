"""Fake service layer for multi-violation test.

Expected violation:
- service -> api
"""

from api.v1.endpoints.bc_multi_endpoint import bc_multi_endpoint


def bc_multi_service(symbol: str) -> dict:
    return bc_multi_endpoint(symbol)
