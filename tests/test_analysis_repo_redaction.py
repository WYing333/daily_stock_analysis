# -*- coding: utf-8 -*-
"""AnalysisRepository 脱敏视图测试。

使用轻量级的数据库存根（stub），避免依赖真实数据库连接。
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.repositories.analysis_repo import AnalysisRepository


class _FakeRecord:
    """模拟 AnalysisHistory，仅暴露 to_dict()。"""

    def __init__(self, payload: Dict[str, Any]):
        self._payload = payload

    def to_dict(self) -> Dict[str, Any]:
        return self._payload


class _FakeDB:
    """模拟 DatabaseManager.get_analysis_history。"""

    def __init__(self, records: List[_FakeRecord]):
        self._records = records

    def get_analysis_history(self, query_id=None, limit=1, **kwargs):
        return self._records


def test_get_redacted_record_redacts_sensitive_keys():
    payload = {
        "id": 1,
        "query_id": "q-1",
        "code": "600519",
        "context_snapshot": {
            "api_key": "sk-super-secret-value",
            "note": "正常文本，不应被脱敏",
        },
    }
    repo = AnalysisRepository(db_manager=_FakeDB([_FakeRecord(payload)]))

    safe = repo.get_redacted_record("q-1")

    assert safe is not None
    assert safe["context_snapshot"]["api_key"] == "[REDACTED]"
    assert safe["context_snapshot"]["note"] == "正常文本，不应被脱敏"
    assert safe["code"] == "600519"


def test_get_redacted_record_missing_returns_none():
    repo = AnalysisRepository(db_manager=_FakeDB([]))

    assert repo.get_redacted_record("missing") is None
