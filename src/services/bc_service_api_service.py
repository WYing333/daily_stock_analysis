"""Fake service layer that imports API layer.

Expected violation:
- service -> api
"""

from api.v1.endpoints.bc_service_api_endpoint import api_helper


def bc_service_api_service(symbol: str) -> dict:
    return api_helper(symbol)
