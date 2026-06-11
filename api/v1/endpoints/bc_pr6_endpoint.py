"""API file with two violated boundaries.

Expected violations:
- api -> data
- api -> integration
"""

from src.repositories.bc_pr6_repo import load_pr6_data
from src.integrations.bc_pr6_integration import call_pr6_external


def bc_pr6_endpoint(symbol: str) -> dict:
    return {
        "data": load_pr6_data(symbol),
        "external": call_pr6_external(symbol),
    }
