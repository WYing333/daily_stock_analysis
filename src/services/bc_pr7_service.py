"""Service file with two violated boundaries.

Expected violations:
- service -> api
- service -> entry
"""

from api.v1.endpoints.bc_pr7_endpoint import pr7_api_helper
from scripts.bc_pr7_entry import pr7_entry_helper


def bc_pr7_service(symbol: str) -> dict:
    return {
        "api": pr7_api_helper(symbol),
        "entry": pr7_entry_helper(symbol),
    }
