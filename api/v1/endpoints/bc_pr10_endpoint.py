"""API file for PR10.

Expected violation:
- api -> data
"""

from src.repositories.bc_pr10_repo import pr10_repo_helper


def pr10_api_helper(symbol: str) -> dict:
    return pr10_repo_helper(symbol)
