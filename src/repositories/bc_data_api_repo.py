"""Fake data layer that imports API layer.

Expected violation:
- data -> api
"""

from api.v1.endpoints.bc_data_api_endpoint import endpoint_helper


def bc_data_api_repo(symbol: str) -> dict:
    return endpoint_helper(symbol)
