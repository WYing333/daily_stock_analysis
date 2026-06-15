"""Service file with two intended boundary violations.

Expected violations:
- service -> api
- service -> entry
"""

from api.v1.endpoints.bc_pr7_endpoint import pr7_api_helper
import main as app_entry


def bc_pr7_service(symbol: str) -> dict:
    return {
        "api": pr7_api_helper(symbol),
        "entry_module": app_entry.__name__,
    }
