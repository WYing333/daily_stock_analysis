"""Domain file with two violated boundaries.

Expected violations:
- domain -> service
- domain -> data
"""

from src.services.bc_pr9_service import pr9_service_helper
from src.repositories.bc_pr9_repo import pr9_repo_helper


def bc_pr9_domain(symbol: str) -> dict:
    return {
        "service": pr9_service_helper(symbol),
        "data": pr9_repo_helper(symbol),
    }
