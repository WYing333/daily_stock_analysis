"""Data file with two violated boundaries.

Expected violations:
- data -> api
- data -> service
"""

from api.v1.endpoints.bc_pr8_endpoint import pr8_api_helper
from src.services.bc_pr8_service import pr8_service_helper


def bc_pr8_repo(symbol: str) -> dict:
    return {
        "api": pr8_api_helper(symbol),
        "service": pr8_service_helper(symbol),
    }
