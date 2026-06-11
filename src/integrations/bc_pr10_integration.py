"""Integration file with two violated boundaries.

Expected violations:
- integration -> api
- integration -> service
"""

from api.v1.endpoints.bc_pr10_endpoint import pr10_api_helper
from src.services.bc_pr10_service import pr10_service_helper


def bc_pr10_integration(symbol: str) -> dict:
    return {
        "api": pr10_api_helper(symbol),
        "service": pr10_service_helper(symbol),
    }
